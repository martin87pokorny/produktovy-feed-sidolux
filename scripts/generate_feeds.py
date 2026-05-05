"""
Generátor produktových feedů — multi-profile XML exporter.

Načte všechna data z Airtable Produkty_v2, pro každý profil v config/profiles/
projde filter a vyrenderuje XML do data/output/.

Použití:
    python scripts/generate_feeds.py                          # všechny profily
    python scripts/generate_feeds.py --profile heureka_general_cz
    python scripts/generate_feeds.py --list-profiles
    python scripts/generate_feeds.py --validate-only          # nezapisovat XML
    python scripts/generate_feeds.py --skip-patchback         # nezapsat stav do AT
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))

from feed import (  # noqa: E402
    apply_filter,
    fetch_catalog,
    list_profiles,
    load_env,
    load_profile,
    render_xml,
    validate_feed,
)
from feed.filters import FilterResult  # noqa: E402

OUTPUT_DIR = ROOT / 'data' / 'output'
PROFILE_INDEX_TABLE = 'Feed_profile_index'


def _ts() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H-%M-%SZ')


def _patchback_index(env: dict, profile_name: str, public_url: str | None,
                     count: int, status: str, summary: str) -> None:
    """Upsert metadat o profilu do tabulky Feed_profile_index."""
    base = env['AIRTABLE_BASE_ID']
    token = env['AIRTABLE_TOKEN']

    # Najít existující řádek dle pole 'Profil'
    formula = f"{{Profil}}='{profile_name}'"
    qs = urllib.parse.urlencode([('filterByFormula', formula), ('maxRecords', '1')])
    url = f'https://api.airtable.com/v0/{base}/{urllib.parse.quote(PROFILE_INDEX_TABLE)}?{qs}'
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        existing = json.loads(resp.read()).get('records', [])

    fields = {
        'Profil': profile_name,
        'Aktivní': True,
        'Posl. regenerace': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'Počet produktů': count,
        'Status posl. běhu': status,
        'Posl. log': summary[:90000],
    }
    if public_url:
        fields['Output URL'] = public_url

    if existing:
        rec_id = existing[0]['id']
        url = f'https://api.airtable.com/v0/{base}/{urllib.parse.quote(PROFILE_INDEX_TABLE)}/{rec_id}'
        body = json.dumps({'fields': fields}).encode()
        req = urllib.request.Request(url, data=body, method='PATCH',
                                      headers={'Authorization': f'Bearer {token}',
                                               'Content-Type': 'application/json'})
    else:
        url = f'https://api.airtable.com/v0/{base}/{urllib.parse.quote(PROFILE_INDEX_TABLE)}'
        body = json.dumps({'records': [{'fields': fields}]}).encode()
        req = urllib.request.Request(url, data=body, method='POST',
                                      headers={'Authorization': f'Bearer {token}',
                                               'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        resp.read()


def main() -> int:
    sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser()
    ap.add_argument('--profile', default='all',
                    help="'all' (default) nebo jméno konkrétního profilu")
    ap.add_argument('--list-profiles', action='store_true')
    ap.add_argument('--validate-only', action='store_true',
                    help="Vyrenderovat in-memory a validovat, nezapsat XML soubor")
    ap.add_argument('--output-dir', type=Path, default=OUTPUT_DIR)
    ap.add_argument('--skip-patchback', action='store_true',
                    help="Nezapsat stav do AT Feed_profile_index")
    ap.add_argument('--public-url-base', default=None,
                    help="Veřejný URL prefix, ze kterého se Output URL skládá "
                         "(např. https://martin87pokorny.github.io/produktovy-feed-sidolux/)")
    args = ap.parse_args()

    profiles_available = list_profiles()
    print(f'Dostupné profily: {profiles_available}')

    if args.list_profiles:
        return 0

    if args.profile == 'all':
        targets = profiles_available
    else:
        if args.profile not in profiles_available:
            print(f'CHYBA: profil {args.profile!r} nenalezen.')
            return 2
        targets = [args.profile]

    if not targets:
        print('CHYBA: žádné profily k běhu.')
        return 2

    env = load_env()
    print('Načítám katalog z Airtable...')
    catalog = fetch_catalog(env)
    print(f'  {len(catalog)} produktů, fetched_at={catalog.fetched_at}')
    args.output_dir.mkdir(parents=True, exist_ok=True)

    overall_ok = True
    summary_index = []

    for profile_name in targets:
        print(f'\n=== Profil: {profile_name} ===')
        profile = load_profile(profile_name)

        included: list = []
        skipped: list[tuple[str, str]] = []
        for product in catalog:
            res: FilterResult = apply_filter(product, profile_name, profile.filter)
            if res.included:
                included.append(product)
            else:
                skipped.append((product.get('Kód Lakma') or product.record_id, res.reason))

        print(f'  Filter: {len(included)} včetně, {len(skipped)} vynecháno')

        if not included:
            print('  ⚠ Žádný produkt neprošel filterm. Skip render.')
            for kod, reason in skipped[:10]:
                print(f'    - {kod}: {reason}')
            if len(skipped) > 10:
                print(f'    ... a dalších {len(skipped) - 10}')

            if not args.skip_patchback:
                summary = f'0 zařazeno, {len(skipped)} vynecháno. Příklady:\n'
                for kod, reason in skipped[:5]:
                    summary += f'  {kod}: {reason}\n'
                try:
                    public_url = None
                    if args.public_url_base:
                        public_url = args.public_url_base.rstrip('/') + '/' + profile.output_filename
                    _patchback_index(env, profile_name, public_url, 0, 'Warning', summary)
                    print('  → patchback: Warning (0 záznamů)')
                except Exception as e:
                    print(f'  ⚠ patchback failed: {e}')
            continue

        xml_bytes, render_stats = render_xml(included, profile)
        print(f'  Render: included={render_stats["included"]}, '
              f'missing_required={render_stats["skipped_missing_required"]}')

        report = validate_feed(xml_bytes, item_element=profile.item_element,
                                expect_min_items=1)
        if not report.ok:
            print(f'  ❌ Validace FAILED:')
            for e in report.errors:
                print(f'     {e}')
            overall_ok = False
        if report.warnings:
            print(f'  ⚠ {len(report.warnings)} warning(s):')
            for w in report.warnings[:5]:
                print(f'     {w}')

        if not args.validate_only:
            out_path = args.output_dir / profile.output_filename
            out_path.write_bytes(xml_bytes)
            print(f'  → {out_path}  ({len(xml_bytes)} B)')

        # Warnings log
        if skipped or render_stats['skipped_missing_required']:
            warn_path = args.output_dir / f'feed_warnings_{profile_name}_{_ts()}.log'
            with warn_path.open('w', encoding='utf-8') as f:
                f.write(f'Profile: {profile_name}\n')
                f.write(f'Catalog: {len(catalog)}, included: {render_stats["included"]}\n\n')
                f.write('=== Vyřazeno filterem ===\n')
                for kod, reason in skipped:
                    f.write(f'  {kod}: {reason}\n')
                f.write('\n=== Vyřazeno (chybí required tag) ===\n')
                for kod, missing in render_stats['skipped_reasons']:
                    f.write(f'  {kod}: missing={missing}\n')
            print(f'  → {warn_path}')

        # Patchback do AT
        if not args.skip_patchback:
            status = 'OK' if report.ok and not report.warnings else ('Warning' if report.ok else 'Error')
            summary = (
                f'Catalog: {len(catalog)}\n'
                f'Filter: {len(included)} zařazeno, {len(skipped)} vynecháno\n'
                f'Render: {render_stats["included"]} OK, '
                f'{render_stats["skipped_missing_required"]} chybí required\n'
                f'Validace: errors={len(report.errors)}, warnings={len(report.warnings)}\n'
            )
            try:
                public_url = None
                if args.public_url_base:
                    public_url = args.public_url_base.rstrip('/') + '/' + profile.output_filename
                _patchback_index(env, profile_name, public_url,
                                 render_stats['included'], status, summary)
                print(f'  → patchback: {status}')
            except Exception as e:
                print(f'  ⚠ patchback failed: {e}')

        summary_index.append({
            'profile': profile_name,
            'output_filename': profile.output_filename,
            'count': render_stats['included'],
            'status': 'OK' if report.ok else 'Error',
        })

    # feed_index.json (rozcestník pro odběratele)
    if not args.validate_only and summary_index:
        idx_path = args.output_dir / 'feed_index.json'
        idx_path.write_text(json.dumps({
            'generated_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
            'feeds': summary_index,
        }, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'\n→ {idx_path}')

    return 0 if overall_ok else 1


if __name__ == '__main__':
    sys.exit(main())
