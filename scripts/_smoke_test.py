"""
Smoke test rendereru bez Airtable. Pouští se ručně:
    python scripts/_smoke_test.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
sys.stdout.reconfigure(encoding='utf-8')

from feed import (
    Product,
    apply_filter,
    load_profile,
    render_xml,
    validate_feed,
)

mock_products = [
    Product(record_id='recA', fields={
        'Kód Lakma': '1010101',
        'Web název CZ': 'Sidolux Universal Marseille soap 1000 ml',
        'Web název SK': 'Sidolux Universal Marseille soap 1000 ml',
        'URL produktu CZ': 'https://www.sidolux.cz/cs-cz/produkty/sidolux-universal-marseille-soap-1000ml',
        'URL produktu SK': 'https://www.sidolux.cz/sk-sk/produkty/sidolux-universal-marseille-soap-1000ml',
        'Cena CZK doporučená': 79.90,
        'Cena EUR doporučená': 3.29,
        'Heureka kategorie CZ': 'Heureka.cz | Drogerie | Čisticí prostředky | Univerzální čisticí prostředky',
        'Heureka kategorie SK': 'Heureka.sk | Drogéria | Čistiace prostriedky | Univerzálne čistiace prostriedky',
        'EAN KS': '5900536001234',
        'Web popis CZ': '<p>Univerzální čistič na <b>všechny mycí povrchy</b>.</p><p>Bez šmouh.</p>',
        'Web popis SK': '<p>Univerzálny čistič na <b>všetky umývateľné povrchy</b>.</p>',
        'Itemgroup ID': 'sidolux-universal-1000ml',
        'Vůně': 'Marseille soap',
        'Objem': '1000ml',
        'Vhodné povrchy': 'podlahy, dlaždice, sklo',
        'Hlavní technologie': 'no-rinse formula',
        'Foto 800×800': [{'url': 'https://attachments.airtableusercontent.com/foo/bar.jpg', 'filename': 'a.jpg'}],
        'Galerie produktu': [
            {'url': 'https://attachments.airtableusercontent.com/foo/g1.jpg'},
            {'url': 'https://attachments.airtableusercontent.com/foo/g2.jpg'},
        ],
        'Přidat do feedu': 'Ano',
        'Feed profily': ['heureka_general_cz', 'heureka_general_sk'],
    }),
    Product(record_id='recB', fields={
        'Kód Lakma': '1020202',
        'Web název CZ': 'Sidolux Window 500 ml',
        'Web název SK': 'Sidolux Window 500 ml',
        'URL produktu CZ': 'https://www.sidolux.cz/cs-cz/produkty/sidolux-window-500ml',
        'URL produktu SK': 'https://www.sidolux.cz/sk-sk/produkty/sidolux-window-500ml',
        'Cena CZK doporučená': 49.90,
        'Cena EUR doporučená': 2.09,
        'Heureka kategorie CZ': 'Heureka.cz | Drogerie | Čisticí prostředky | Čistící prostředky na okna a skla',
        'Heureka kategorie SK': 'Heureka.sk | Drogéria | Čistiace prostriedky | Čistiace prostriedky na okná a sklá',
        'EAN KS': '5900536009999',
        'Objem': '500ml',
        'Foto 800×800': [{'url': 'https://attachments.airtableusercontent.com/foo/window.jpg'}],
        'Přidat do feedu': 'Ano',
        'Feed profily': ['heureka_general_cz', 'heureka_general_sk'],
    }),
]

for profile_name in ('heureka_general_cz', 'heureka_general_sk'):
    print(f'\n=== {profile_name} ===')
    profile = load_profile(profile_name)
    included = []
    for p in mock_products:
        res = apply_filter(p, profile_name, profile.filter)
        print(f'  {p.get("Kód Lakma")}: included={res.included}  reason={res.reason!r}')
        if res.included:
            included.append(p)

    xml_bytes, stats = render_xml(included, profile)
    print(f'  Render stats: {stats}')

    report = validate_feed(xml_bytes, item_element=profile.item_element)
    print(f'  Valid: ok={report.ok}, errors={report.errors}, warnings={len(report.warnings)}')
    for w in report.warnings:
        print(f'    WARN {w}')

    print('\n--- XML preview ---')
    print(xml_bytes.decode('utf-8'))
    print('-'*60)
