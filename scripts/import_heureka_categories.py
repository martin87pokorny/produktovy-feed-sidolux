"""
Import Heureka kategorií CZ/SK z CSV do Airtable Produkty_v2.

Vstup:  data/heureka_categories/heureka_category_import_2026-05-05.csv
Cíl:    pole 'Heureka kategorie CZ' a 'Heureka kategorie SK'
Default --dry-run = OFF (naostro). Pro preview spusť s --dry-run.
"""
import argparse
import csv
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / '.env'
DEFAULT_CSV = ROOT / 'data' / 'heureka_categories' / 'heureka_category_import_2026-05-05.csv'

FIELD_CZ = 'Heureka kategorie CZ'
FIELD_SK = 'Heureka kategorie SK'
FIELD_KOD = 'Kód Lakma'


def load_env():
    env = {}
    with ENV_PATH.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            env[k.strip()] = v.split('  ')[0].strip()
    return env


def airtable_get(url, token):
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def fetch_all(token, base, table):
    fields = [FIELD_KOD, FIELD_CZ, FIELD_SK]
    records = []
    offset = None
    while True:
        params = [('pageSize', '100')]
        for f in fields:
            params.append(('fields[]', f))
        if offset:
            params.append(('offset', offset))
        url = f'https://api.airtable.com/v0/{base}/{urllib.parse.quote(table)}?{urllib.parse.urlencode(params)}'
        data = airtable_get(url, token)
        records.extend(data.get('records', []))
        offset = data.get('offset')
        if not offset:
            break
    return records


def load_csv(path):
    rows = []
    with path.open('r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            rows.append({
                'kod': row[FIELD_KOD].strip(),
                'cz': row[FIELD_CZ].strip(),
                'sk': row[FIELD_SK].strip(),
            })
    return rows


def patch_batch(url, token, batch):
    body = json.dumps({'records': batch}).encode('utf-8')
    req = urllib.request.Request(url, data=body, method='PATCH',
                                  headers={'Authorization': f'Bearer {token}',
                                           'Content-Type': 'application/json'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            body_text = e.read().decode('utf-8', errors='replace')
            if e.code == 429 and attempt < 2:
                time.sleep(2 * (attempt + 1))
                continue
            raise RuntimeError(f'HTTP {e.code}: {body_text[:400]}')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true', help='Jen preview, nezapisovat')
    ap.add_argument('--csv', type=Path, default=DEFAULT_CSV)
    args = ap.parse_args()

    print(f'CSV: {args.csv}')
    print(f'Mód: {"DRY-RUN" if args.dry_run else "LIVE PATCH"}')
    print()

    env = load_env()
    token = env['AIRTABLE_TOKEN']
    base = env['AIRTABLE_BASE_ID']
    table = env['AIRTABLE_TABLE_NAME']

    csv_rows = load_csv(args.csv)
    print(f'CSV řádků: {len(csv_rows)}')

    records = fetch_all(token, base, table)
    print(f'Airtable záznamů: {len(records)}')

    by_kod = {}
    for r in records:
        kod = r['fields'].get(FIELD_KOD)
        if kod:
            by_kod[kod] = r

    # Pre-flight: ověření existence polí na sample záznamu
    sample_fields = set()
    for r in records[:5]:
        sample_fields.update(r['fields'].keys())
    # AT vrací jen vyplněná pole, takže absence v sample neznamená neexistenci.
    # Skutečná detekce neexistujícího pole proběhne při PATCH (HTTP 422).

    missing = [row['kod'] for row in csv_rows if row['kod'] not in by_kod]
    if missing:
        print(f'CHYBA: v AT chybí {len(missing)} produktů z CSV: {missing[:10]}')
        sys.exit(2)

    patches = []
    new_cz = overwrite_cz = same_cz = 0
    new_sk = overwrite_sk = same_sk = 0
    samples = []

    for row in csv_rows:
        rec = by_kod[row['kod']]
        cur_cz = rec['fields'].get(FIELD_CZ, '')
        cur_sk = rec['fields'].get(FIELD_SK, '')
        new_fields = {}

        if cur_cz != row['cz']:
            new_fields[FIELD_CZ] = row['cz']
            if cur_cz:
                overwrite_cz += 1
            else:
                new_cz += 1
        else:
            same_cz += 1

        if cur_sk != row['sk']:
            new_fields[FIELD_SK] = row['sk']
            if cur_sk:
                overwrite_sk += 1
            else:
                new_sk += 1
        else:
            same_sk += 1

        if new_fields:
            patches.append({'id': rec['id'], 'fields': new_fields})
            if len(samples) < 5:
                samples.append((row['kod'], cur_cz, row['cz'], cur_sk, row['sk']))

    print()
    print('=== Souhrn diffu ===')
    print(f'  CZ: nově={new_cz}  přepis={overwrite_cz}  beze změny={same_cz}')
    print(f'  SK: nově={new_sk}  přepis={overwrite_sk}  beze změny={same_sk}')
    print(f'  Patches celkem (záznamy ke změně): {len(patches)}')

    if samples:
        print()
        print('=== Sample (max 5) ===')
        for kod, ccz, ncz, csk, nsk in samples:
            print(f'  {kod}')
            print(f'    CZ: {ccz!r:60}  ->  {ncz!r}')
            print(f'    SK: {csk!r:60}  ->  {nsk!r}')

    if not patches:
        print('\nNic ke změně, končím.')
        return

    if args.dry_run:
        print('\nDRY-RUN — žádný zápis. Pro provedení spusť bez --dry-run.')
        return

    url = f'https://api.airtable.com/v0/{base}/{urllib.parse.quote(table)}'
    success = 0
    for i in range(0, len(patches), 10):
        batch = patches[i:i+10]
        try:
            rj = patch_batch(url, token, batch)
            success += len(rj.get('records', []))
            print(f'  batch {i//10+1}/{(len(patches)+9)//10}: OK ({len(rj.get("records", []))} rec)')
        except RuntimeError as e:
            print(f'  batch {i//10+1}: FAIL - {e}')
        time.sleep(0.25)

    print(f'\nPushed: {success}/{len(patches)}')

    # Re-fetch a kontrola
    print('\n=== Verifikace ===')
    records = fetch_all(token, base, table)
    by_kod = {r['fields'].get(FIELD_KOD): r for r in records if r['fields'].get(FIELD_KOD)}
    mismatch = []
    filled_cz = filled_sk = 0
    for row in csv_rows:
        rec = by_kod.get(row['kod'])
        if not rec:
            continue
        f = rec['fields']
        if f.get(FIELD_CZ) == row['cz']:
            filled_cz += 1
        else:
            mismatch.append((row['kod'], 'CZ', f.get(FIELD_CZ), row['cz']))
        if f.get(FIELD_SK) == row['sk']:
            filled_sk += 1
        else:
            mismatch.append((row['kod'], 'SK', f.get(FIELD_SK), row['sk']))
    print(f'  CZ shoda: {filled_cz}/{len(csv_rows)}')
    print(f'  SK shoda: {filled_sk}/{len(csv_rows)}')
    if mismatch:
        print(f'  Neshody ({len(mismatch)}):')
        for m in mismatch[:10]:
            print(f'    {m}')


if __name__ == '__main__':
    main()
