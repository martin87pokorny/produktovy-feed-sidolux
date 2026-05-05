# Sidolux / Lakma — Produktový feed

Generování XML feedu pro **Heureka.cz** a **Heureka.sk** ze 143 produktů řady Sidolux.

> **Klient:** Lakma (výrobce, Polsko) → distribuce přes Drogerie ZDE
> **Není e-shop:** ceny ve feedu jsou jen doporučené MOC (porovnávač).
> **Zdrojová data:** Airtable base `appSIEtMDgBsBPpjS`, tabulka `Produkty_v2`.

---

## Stav projektu

| Fáze | Stav |
|------|------|
| **1. Struktura dat v Airtable** | ✅ hotová (URL, Itemgroup ID, EAN KS/KRT, Web slug) |
| **1b. Heureka kategorizace** | ✅ zapsaná v AT (142/143, Q Power 1014009 vyřazen) |
| **2. Doplnění cen + dalších údajů** | ⏳ odeslán Excel pro výrobce (`data/exchange/cenik_pro_vyrobce_*.xlsx`), čeká se na vyplnění |
| **3. Generátor feedu** | 🔜 po doplnění cen |
| **4. Hosting + automatický refresh** | 🔜 |

Detailní plán v [`docs/plan_feed.md`](docs/plan_feed.md).

---

## Adresářová struktura

```
.
├── .env                          # API token Airtable (mimo Git)
├── README.md                     # tento soubor
├── AGENT.md                      # pravidla pro AI agenty
├── CLAUDE.md                     # specifické pravidla pro Claude Code
├── scripts/
│   ├── fill_feed_data.py         # vyplní auto-odvoditelná pole (URL, Itemgroup, kategorie)
│   ├── generate_pricing_excel.py # vygeneruje Excel pro výrobce
│   ├── import_pricing.py         # 🔜 import vyplněného Excelu zpět do Airtable
│   └── generate_heureka_feed.py  # 🔜 hlavní generátor XML feedu (CZ + SK)
├── data/
│   ├── exchange/                 # výměna s výrobcem (Excel ven, vyplněný zpět)
│   ├── output/                   # vygenerované feedy (heureka_cz.xml, heureka_sk.xml)
│   └── reference/                # referenční data
│       └── logistika_kamil/      # logistická tabulka 2026-04-09 od Kamila
├── docs/
│   └── plan_feed.md              # plán, mapování polí, otevřené otázky
└── memory/
    └── MEMORY.md                 # paměť pro Claude Code (kontext napříč sessionami)
```

---

## Navigace pro lidi

- **Naplánovat / pochopit kontext** → [`docs/plan_feed.md`](docs/plan_feed.md)
- **Heureka kategorie CZ/SK připravené k nasazení do AT** → [`docs/heureka_categories.md`](docs/heureka_categories.md)
- **Pravidla pro AI** → [`AGENT.md`](AGENT.md)
- **Pustit existující skript** → `scripts/<jmeno>.py`
- **Najít vyplněný ceník od výrobce** → `data/exchange/`
- **Otevřít vygenerovaný feed** → `data/output/heureka_cz.xml` (po vygenerování)

## Navigace pro AI agenty

1. Začni přečtením [`AGENT.md`](AGENT.md) (kontrakt, scope, do/don't)
2. Pak [`docs/plan_feed.md`](docs/plan_feed.md) (mapování Heureka → Airtable, co chybí)
3. [`memory/MEMORY.md`](memory/MEMORY.md) (zkušenosti z předchozích sessionů)

---

## Související projekty

- **Popisy produktů Sidolux** — `../Popisy_Produkty_Sidolux/`
  Generování CZ/SK marketingových popisů a jejich review workflow. **Tento projekt (feed) sahá do Airtable po stejných datech**, ale **nemění Web pole / drafty / popisy** — ty řeší sourozenecký projekt. Feed čerpá hotové, schválené texty.

---

## Závislosti

- Python 3.13+
- `openpyxl` 3.1+ (pro Excel)
- Žádné další balíčky — Airtable přes `urllib` ze stdlib

## Přístupy

- **Airtable PAT** v `.env` (`AIRTABLE_TOKEN`, `AIRTABLE_BASE_ID`, `AIRTABLE_TABLE_NAME`)
  Scope: `data.records:read`, `data.records:write`, `schema.bases:write` (pro vytváření polí).
- **Webflow CDN** pro Foto URL — řeší se ve Fázi 2/3.

## Kontakt

honza@drogeriezde.cz
