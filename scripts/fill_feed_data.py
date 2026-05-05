"""
Naplní automaticky odvoditelná pole pro Heureka feed:
- URL produktu CZ/SK ze slug
- Itemgroup ID (řada+objem) pro varianty 2+
- Heureka kategorie CZ/SK podle Web produktová řada CZ
"""
import json
import sys
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent.parent / '.env'

HEUREKA_CZ = {
    'Sidolux UNIVERSAL':              'Drogerie | Úklid | Univerzální čističe',
    'Sidolux PREMIUM FLOOR CARE':     'Drogerie | Úklid | Čističe podlah',
    'Sidolux EXPERT':                 'Drogerie | Úklid | Čističe podlah',
    'Sidolux ECO':                    'Drogerie | Úklid | Univerzální čističe',
    'Sidolux WINDOW':                 'Drogerie | Úklid | Čističe oken',
    'Sidolux M péče o nábytek':       'Drogerie | Úklid | Čističe a leštidla na nábytek',
    'Sidolux PROFESSIONAL':           'Drogerie | Úklid | Čističe na specifické nečistoty',
    'Sidolux Praní':                  'Drogerie | Praní | Prací prostředky',
    'PERLUX':                         'Drogerie | Praní | Prací prostředky',
    'MR. TEPPICH':                    'Drogerie | Úklid | Čističe koberců',
    'SILUX WC':                       'Drogerie | Úklid | WC čističe',
    'Silux':                          'Drogerie | Úklid | Houbičky a utěrky',
}

HEUREKA_SK = {
    'Sidolux UNIVERSAL':              'Drogéria | Upratovanie | Univerzálne čističe',
    'Sidolux PREMIUM FLOOR CARE':     'Drogéria | Upratovanie | Čističe podláh',
    'Sidolux EXPERT':                 'Drogéria | Upratovanie | Čističe podláh',
    'Sidolux ECO':                    'Drogéria | Upratovanie | Univerzálne čističe',
    'Sidolux WINDOW':                 'Drogéria | Upratovanie | Čističe okien',
    'Sidolux M péče o nábytek':       'Drogéria | Upratovanie | Čističe a leštidlá na nábytok',
    'Sidolux PROFESSIONAL':           'Drogéria | Upratovanie | Čističe na špecifické nečistoty',
    'Sidolux Praní':                  'Drogéria | Pranie | Pracie prostriedky',
    'PERLUX':                         'Drogéria | Pranie | Pracie prostriedky',
    'MR. TEPPICH':                    'Drogéria | Upratovanie | Čističe kobercov',
    'SILUX WC':                       'Drogéria | Upratovanie | WC čističe',
    'Silux':                          'Drogéria | Upratovanie | Hubky a utierky',
}

DIA_MAP = str.maketrans(
    'áčďéěíňóřšťúůýžÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ',
    'acdeeinorstuuyzACDEEINORSTUUYZ'
)


def slugify_rada(s: str) -> str:
    return s.lower().translate(DIA_MAP).replace(' ', '-').replace('.', '').replace('/', '-').replace('--', '-')


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


def fetch_records(token, base, table):
    fields = ['Kód Lakma', 'Web slug', 'Web produktová řada CZ', 'Objem',
              'URL produktu CZ', 'URL produktu SK', 'Itemgroup ID',
              'Heureka kategorie CZ', 'Heureka kategorie SK']
    records = []
    offset = None
    while True:
        params = [('pageSize', '100')]
        for f in fields:
            params.append(('fields[]', f))
        if offset:
            params.append(('offset', offset))
        qs = urllib.parse.urlencode(params)
        url = f'https://api.airtable.com/v0/{base}/{urllib.parse.quote(table)}?{qs}'
        req = urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        records.extend(data.get('records', []))
        offset = data.get('offset')
        if not offset:
            break
    return records


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    env = load_env()
    token, base, table = env['AIRTABLE_TOKEN'], env['AIRTABLE_BASE_ID'], env['AIRTABLE_TABLE_NAME']

    records = fetch_records(token, base, table)
    print(f'Stáhnuto {len(records)} produktů')
    slug_filled = sum(1 for r in records if r['fields'].get('Web slug'))
    print(f'  s Web slug: {slug_filled}/{len(records)}')

    # Skupiny řada+objem s 2+ produkty -> Itemgroup ID kandidáti
    group_count = defaultdict(list)
    for r in records:
        f = r['fields']
        rada = f.get('Web produktová řada CZ', '')
        obj = f.get('Objem', '')
        if rada and obj:
            group_count[(rada, obj)].append((f.get('Kód Lakma'), f.get('Web slug', '')))

    candidates = {}
    print('\n=== Skupiny řada+objem 2+ produktů (Itemgroup ID kandidáti) ===')
    for (rada, obj), items in sorted(group_count.items()):
        if len(items) >= 2:
            gid = f'{slugify_rada(rada)}-{obj.lower()}'
            candidates[(rada, obj)] = gid
            print(f'  {gid}  ({len(items)}x)')

    # Naplnit
    patches = []
    report = {'url_cz': 0, 'url_sk': 0, 'igid': 0, 'cat_cz': 0, 'cat_sk': 0}
    no_slug = []
    no_rada_mapping = set()

    for r in records:
        f = r['fields']
        kod = f.get('Kód Lakma', '')
        rada = f.get('Web produktová řada CZ', '')
        obj = f.get('Objem', '')
        slug = f.get('Web slug', '')
        new = {}

        if not f.get('URL produktu CZ') and slug:
            new['URL produktu CZ'] = f'https://www.sidolux.cz/cs-cz/produkty/{slug}'
            report['url_cz'] += 1
        if not f.get('URL produktu SK') and slug:
            new['URL produktu SK'] = f'https://www.sidolux.cz/sk-sk/produkty/{slug}'
            report['url_sk'] += 1
        if not slug:
            no_slug.append(kod)

        if not f.get('Itemgroup ID') and (rada, obj) in candidates:
            new['Itemgroup ID'] = candidates[(rada, obj)]
            report['igid'] += 1

        if rada:
            if not f.get('Heureka kategorie CZ'):
                if rada in HEUREKA_CZ:
                    new['Heureka kategorie CZ'] = HEUREKA_CZ[rada]
                    report['cat_cz'] += 1
                else:
                    no_rada_mapping.add(rada)
            if not f.get('Heureka kategorie SK'):
                if rada in HEUREKA_SK:
                    new['Heureka kategorie SK'] = HEUREKA_SK[rada]
                    report['cat_sk'] += 1

        if new:
            patches.append({'id': r['id'], 'fields': new})

    print(f'\n=== K naplnění ===')
    for k, v in report.items():
        print(f'  {k}: {v}')
    print(f'  patches total: {len(patches)} záznamů')
    if no_slug:
        print(f'\nProdukty BEZ Web slug ({len(no_slug)}): {no_slug}')
    if no_rada_mapping:
        print(f'\nŘady BEZ Heureka mapování: {sorted(no_rada_mapping)}')

    # Push
    url = f'https://api.airtable.com/v0/{base}/{urllib.parse.quote(table)}'
    success = 0
    for i in range(0, len(patches), 10):
        batch = patches[i:i+10]
        body = json.dumps({'records': batch}).encode('utf-8')
        req = urllib.request.Request(url, data=body, method='PATCH',
                                      headers={'Authorization': f'Bearer {token}',
                                               'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                rj = json.loads(resp.read())
            success += len(rj.get('records', []))
        except urllib.error.HTTPError as e:
            b = e.read().decode('utf-8', errors='replace')
            print(f'  batch {i//10+1}: HTTP {e.code} – {b[:300]}')
        time.sleep(0.25)
    print(f'\nPushed: {success}/{len(patches)}')


if __name__ == '__main__':
    main()
