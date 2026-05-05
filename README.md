# Sidolux / Lakma — Produktový feed

Multi-profile XML produktový feed pro **B2B odběratele** (143 SKU řady Sidolux).
Default schema = Heureka XML Feed; custom profily pro konkrétní odběratele
se přidávají jako JSON soubory v `config/profiles/`.

> **Klient:** Lakma (výrobce, Polsko) → distribuce přes Drogerie ZDE
> **Není e-shop:** ceny jsou doporučené MOC, dopravu řeší odběratel.
> **Zdrojová data:** Airtable base `appSIEtMDgBsBPpjS`, tabulka `Produkty_v2`.

---

## Stav projektu

| Fáze | Stav |
|------|------|
| **1. Struktura dat v Airtable** | ✅ hotová |
| **1b. Heureka kategorizace** | ✅ zapsaná v AT (142/143, Q Power 1014009 vyřazen) |
| **2. Ceník + další údaje** | ⏳ Excel odeslán výrobci, čeká se na vyplnění |
| **3. Generátor feedu** | ✅ multi-profile knihovna + 2 default profily, ověřeno |
| **4. Hosting + auto-refresh** | ✅ GH Pages + GH Action (cron 4h + manual) |
| **5. Distribuce odběratelům** | ✅ docs + URL, AT Automation tlačítko čeká na napojení |

Detailní plán v [`docs/plan_feed.md`](docs/plan_feed.md).

---

## Veřejné URL

- Rozcestník: <https://martin87pokorny.github.io/produktovy-feed-sidolux/>
- CZ feed: <https://martin87pokorny.github.io/produktovy-feed-sidolux/heureka_general_cz.xml>
- SK feed: <https://martin87pokorny.github.io/produktovy-feed-sidolux/heureka_general_sk.xml>
- Repo: <https://github.com/martin87pokorny/produktovy-feed-sidolux>

---

## Adresářová struktura

```
.
├── .env                          # API tokeny (mimo Git)
├── README.md, AGENT.md, CLAUDE.md
├── .github/workflows/
│   └── regenerate_feeds.yml      # cron 4h + workflow_dispatch
├── scripts/
│   ├── feed/                     # knihovna generátoru
│   │   ├── catalog.py            #   AT fetch + Product/ProductCatalog + INTERNAL_FIELDS_BLOCKLIST
│   │   ├── profile.py            #   loader profilů s extends resolution
│   │   ├── filters.py            #   filter engine
│   │   ├── transforms.py         #   html_to_plain, decimal, percent, attachment urls
│   │   ├── renderer.py           #   XML rendering (CDATA, multi-IMGURL, PARAM, extras)
│   │   └── validator.py          #   post-render validace (XML well-formed, EAN, URL, dupes)
│   ├── generate_feeds.py         # entry point: --profile, --list-profiles, --validate-only
│   ├── import_pricing.py         # import vyplněného Excelu od výrobce (cena CZK/EUR)
│   ├── import_heureka_categories.py  # import Heureka kategorií (✅ použito 2026-05-05)
│   ├── generate_pricing_excel.py     # vygeneruje Excel pro výrobce
│   ├── prepare_heureka_category_mapping.py  # mapování řad → Heureka kategorie
│   ├── update_heureka_category_reference.py # stáhne referenční XML z Heureky
│   ├── fill_feed_data.py         # bootstrap polí (URL, Itemgroup) — historický
│   ├── _build_feed_index_html.py # rozcestník index.html (volá GH Action)
│   ├── _notify_at_failure.py     # patch AT na status Error při failu workflow
│   └── _smoke_test.py            # smoke test rendereru s mock daty
├── config/
│   └── profiles/
│       ├── heureka_general_cz.json
│       └── heureka_general_sk.json
├── data/
│   ├── assets/                   # SVG loga GBY (deploy do GH Pages)
│   ├── exchange/                 # výměna s výrobcem (Excel ven, vyplněný zpět)
│   ├── output/                   # vygenerované feedy + warnings + feed_index.json
│   ├── heureka_categories/       # zdroj k importu Heureka kategorií
│   └── reference/                # referenční data (logistika, Heureka XML strom)
├── docs/
│   ├── plan_feed.md              # detailní plán
│   ├── feeds_for_partners.md     # dokumentace pro B2B odběratele
│   ├── at_automation_setup.md    # návod na AT tlačítko regenerace
│   └── heureka_categories.md
└── memory/
    └── MEMORY.md                 # kontextová paměť pro Claude Code
```

---

## Navigace pro lidi

- **Pochopit kontext** → [`docs/plan_feed.md`](docs/plan_feed.md)
- **Pro odběratele (B2B partneři)** → [`docs/feeds_for_partners.md`](docs/feeds_for_partners.md)
- **Pravidla pro AI** → [`AGENT.md`](AGENT.md)
- **Pustit existující skript** → `scripts/<jmeno>.py`
- **Najít vyplněný ceník od výrobce** → `data/exchange/`
- **Otevřít aktuální feed** → veřejné URL výše (lokálně se generují do `data/output/`)
- **Spustit regeneraci on-demand** → `gh workflow run regenerate_feeds.yml --repo martin87pokorny/produktovy-feed-sidolux -f profile=all`

## Navigace pro AI agenty

1. [`AGENT.md`](AGENT.md) — kontrakt, scope, do/don't
2. [`docs/plan_feed.md`](docs/plan_feed.md) — mapování, blokátory
3. [`memory/MEMORY.md`](memory/MEMORY.md) — kontext z předchozích sessionů

---

## Související projekty

- **Popisy produktů Sidolux** — `../Popisy_Produkty_Sidolux/`
  Generování CZ/SK marketingových popisů a jejich review workflow. Sdílí
  stejnou Airtable bázi, ale jiný scope. Feed čerpá schválené texty
  read-only, popisy/drafty/Web pole nemodifikuje.

---

## Závislosti

- Python 3.13+
- `openpyxl` 3.1+ (pro Excel — používá jen `import_pricing.py` a `generate_pricing_excel.py`)
- Žádné další balíčky — Airtable + GitHub přes `urllib` ze stdlib

## Přístupy

- **Airtable PAT** v `.env` (`AIRTABLE_TOKEN`, `AIRTABLE_BASE_ID`, `AIRTABLE_TABLE_NAME`)
  Scope: `data.records:read`, `data.records:write`, `schema.bases:write`.
- **GitHub** přes `gh` CLI auth, scope `repo` + `workflow`.
- **GitHub Actions secrets** (v repu): stejné jako .env (AT credentials).
- **Webflow CDN** pro Foto URL — po Fázi 2.

## Kontakt

- Obsah, sortiment, ceny: **honza@drogeriezde.cz**
- Technická integrace, custom feedy: **martin@gby.agency**
