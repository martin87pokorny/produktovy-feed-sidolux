# Plán produktového feedu

> Stav k **2026-05-06**. MVP technicky hotové, čeká na vstupní data.
> Aktualizuj při každém větším posunu.

## Cíl

Generovat XML produktové feedy ze 143 SKU řady Sidolux pro **B2B odběratele**.
Default formát = **Heureka XML Feed** (široká kompatibilita s odběratelskými
systémy), ale architektura je multi-profile — jeden katalog produktů v AT,
N profilů v `config/profiles/*.json`, N XML výstupů per běh. Custom profily
pro konkrétní odběratele se přidávají jako další JSON.

Klient (Lakma) **není e-shop** — ceny jsou doporučené MOC, dopravu si řeší
odběratel sám (paletová přeprava z centrálního skladu).

---

## Architektura

```
       ┌──────────────────────────┐
       │  Airtable Produkty_v2    │   ← single source of truth
       └────────────┬─────────────┘
                    │ scripts/feed/catalog.py
                    ▼
       ┌──────────────────────────┐
       │  ProductCatalog          │   ← 143× Product objekt
       └────────────┬─────────────┘
                    │
        ┌───────────┼─────────────┐
        ▼           ▼             ▼
   Profil A    Profil B      Custom profil
   heureka_    heureka_      odberatel_X
   general_cz  general_sk    (až bude potřeba)
        │           │             │
        ▼           ▼             ▼
       .xml        .xml          .xml
```

- **Generátor (`scripts/feed/`)** je generic — pracuje s `Product` a `Profile`, ničemu v doméně se nerozhoduje.
- **Profily (`config/profiles/*.json`)** drží logiku — filter, mapping, transformace, extras. Přidání odběratele = přidání jednoho JSON.
- **AT pole `Feed profily`** (multipleSelects) na produktu rozhoduje, do kterých profilů produkt patří.
- **AT tabulka `Feed_profile_index`** je dashboard — generátor sem patchuje status po každém běhu.

Detail viz `scripts/feed/{catalog,profile,filters,transforms,renderer,validator}.py`.

---

## Mapování Heureka tag → Airtable Produkty_v2 (default profil)

| Heureka tag | Povinné? | AT pole | Stav |
|-------------|----------|---------|------|
| ITEM_ID | ✓ | Kód Lakma | ✅ 143/143 |
| PRODUCTNAME | ✓ | Web název CZ / SK | ✅ 143/143 |
| URL | ✓ | URL produktu CZ / SK | ✅ 143/143 |
| PRICE_VAT | ✓ | Cena CZK / EUR doporučená | ⏳ čeká na ceník |
| DESCRIPTION | doporučeno | Web popis CZ / SK | ✅ 143/143 |
| CATEGORYTEXT | doporučeno | Heureka kategorie CZ / SK | ✅ 142/143 v AT (1014009 vyřazen) |
| IMGURL | doporučeno | `Foto 800×800` (provisional) → Webflow CDN | ⏳ |
| IMGURL_ALTERNATIVE | volitelné | `Galerie produktu` → Webflow CDN | ⏳ |
| EAN | povinné pro chemii | EAN KS | ✅ (2× NA) |
| MANUFACTURER | doporučeno | konstanta `Lakma` | ✅ |
| PRODUCTNO | volitelné | MPN (z Excelu) | ⏳ čeká, AT pole zatím není |
| PARAM | doporučeno | Vůně, Objem, Vhodné povrchy, Hlavní technologie | ✅ částečně |
| ITEMGROUP_ID | doporučeno | Itemgroup ID | ✅ 117/143 (zbylých 26 jsou solitéři) |
| DELIVERY_DATE | doporučeno | konstanta `0` | ✅ |
| DELIVERY | doporučeno | — | ❌ záměrně prázdné (B2B feed) |
| VAT | volitelné | konstanta `21%` (CZ) / `23%` (SK) | ✅ |

---

## Filtrace produktu do feedu

Profil `heureka_general_cz` (analogicky SK) zařadí produkt, jen když platí
**všechno**:

1. `Přidat do feedu = "Ano"` (Honza ručně přepíná)
2. `Feed profily` obsahuje `heureka_general_cz` (resp. `_sk`)
3. Vyplněné `URL produktu CZ` (resp. SK)
4. Vyplněná `Cena CZK doporučená` (resp. `Cena EUR doporučená`)
5. Vyplněná `Heureka kategorie CZ` (resp. SK)
6. Validní EAN KS (8/12/13/14 číslic, ne `NA`)

Vynechané produkty se logují do `data/output/feed_warnings_<profile>_<ts>.log`.

---

## Itemgroup ID pravidlo

`{slug-řady}-{objem}` pro produkty, kde se liší jen vůně. Např. všech 21 vůní
`Sidolux Universal 1000ml` má hodnotu `sidolux-universal-1000ml`. Heureka pak
nabízí selektor vůně na 1 produkt. stránce.

---

## Hosting + automatický refresh

- **Repo:** [`martin87pokorny/produktovy-feed-sidolux`](https://github.com/martin87pokorny/produktovy-feed-sidolux) (public)
- **Hosting:** GitHub Pages, branch `gh-pages`
- **URL:** <https://martin87pokorny.github.io/produktovy-feed-sidolux/>
- **Workflow:** `.github/workflows/regenerate_feeds.yml`
  - Cron `0 */4 * * *` (každé 4 hodiny — minimum, které Heureka tolerovala)
  - `workflow_dispatch` s `profile` inputem (`all` / konkrétní jméno)
  - Job summary v Actions UI po každém běhu
  - `if: failure()` step → patchne všechny záznamy v `Feed_profile_index` na status `Error` s odkazem na run
- **Secrets v repu:** `AIRTABLE_TOKEN`, `AIRTABLE_BASE_ID`, `AIRTABLE_TABLE_NAME`
- **Custom doména** `feed.sidolux.cz` — odložené na po MVP

---

## Otevřené blokátory (čeká na vstupní data)

| # | Co | Vlastník | Stav |
|---|----|---------|------|
| 1 | Vyplněný ceník v Excelu | výrobce / Lakma PL | odesláno 2026-05-05, čeká |
| 2 | Webflow CDN URL fotek | web tým | čeká |
| 3 | AT pole `Foto URL CZ` / `Foto URL SK` (přidat až dorazí Webflow) | feed projekt | po doručení URL pattern |
| 4 | AT Automation tlačítko (fine-grained PAT) | Honza + feed projekt | návod v `docs/at_automation_setup.md` |
| 5 | První custom B2B profil pro reálného odběratele | feed projekt | až přijde požadavek |
| 6 | Heureka feed-validator manuální test | Honza | URL feedu už máme, kdykoli |

---

## Co dál (po doručení ceníku)

1. `python scripts/import_pricing.py data/exchange/cenik_VYPLNENY_*.xlsx --dry-run` → review
2. Naostro → 141× cena v AT
3. `gh workflow run regenerate_feeds.yml` (nebo počkat na cron)
4. Stáhnout XML z GH Pages, validovat přes [Heureka feed-validator](https://sluzby.heureka.cz/sluzby/feed-validator/)
5. Případně doladit 3 low-confidence Heureka kategorie (`1011003`, `1011901`, `1011908`)

## Co dál (po doručení Webflow URL)

1. Přidat AT pole `Foto URL CZ` / `Foto URL SK` (singleLineText URL)
2. Hromadně doplnit URL z Webflow (skript / manuální import)
3. Změnit v profilech `IMGURL` source z `Foto 800×800` → `Foto URL CZ`/`Foto URL SK`
4. `gh workflow run` → IMGURL bude stabilní URL

---

## Heureka kategorie — mapování řad (pro referenci)

| Řada | CZ | SK |
|------|-----|-----|
| Sidolux UNIVERSAL | Heureka.cz \| Drogerie \| Čisticí prostředky \| Univerzální čisticí prostředky | Heureka.sk \| Drogéria \| Čistiace prostriedky \| Univerzálne čistiace prostriedky |
| Sidolux ECO | Heureka.cz \| Drogerie \| Ekologická domácnost \| Ekologické čisticí prostředky | Heureka.sk \| Drogéria \| Ekologická domácnosť \| Ekologické čistiace prostriedky |
| Sidolux EXPERT | Heureka.cz \| Drogerie \| Čisticí prostředky \| Leštící prostředky \| Leštidla na podlahy | Heureka.sk \| Drogéria \| Čistiace prostriedky \| Leštiace prostriedky \| Leštidlá na podlahy |
| Sidolux PREMIUM FLOOR CARE | Heureka.cz \| Drogerie \| Čisticí prostředky \| Čistící prostředky na podlahy | Heureka.sk \| Drogéria \| Čistiace prostriedky \| Čistiace prostriedky na podlahy |
| Sidolux WINDOW | Heureka.cz \| Drogerie \| Čisticí prostředky \| Čistící prostředky na okna a skla | Heureka.sk \| Drogéria \| Čistiace prostriedky \| Čistiace prostriedky na okná a sklá |
| Sidolux M péče o nábytek | Heureka.cz \| Drogerie \| Čisticí prostředky \| Leštící prostředky \| Leštidla na nábytek a přípravky proti prachu | Heureka.sk \| Drogéria \| Čistiace prostriedky \| Leštiace prostriedky \| Leštidlá na nábytok a prípravky proti prachu |
| Sidolux PROFESSIONAL | mix podle názvu | mix podle názvu |
| Sidolux Praní + PERLUX | mix podle názvu (gely / kapsle / aviváže / odstraňovače) | mix podle názvu |
| MR. TEPPICH | Heureka.cz \| Drogerie \| Čisticí prostředky \| Čisticí prostředky na koberce a čalounění | Heureka.sk \| Drogéria \| Čistiace prostriedky \| Čistiace prostriedky na koberce a čalúnenie |
| SILUX WC | Heureka.cz \| Drogerie \| Čisticí prostředky \| Dezinfekční prostředky na WC | Heureka.sk \| Drogéria \| Čistiace prostriedky \| Dezinfekčné prostriedky na WC |
| Silux | mix podle názvu (houbičky / utěrky / nábytek) | mix podle názvu |

Detailní mapování v [`docs/heureka_categories.md`](heureka_categories.md). Q Power `1014009` z kategorizace vyřazen.

---

## Souhrnný stav fází

| Fáze | Stav |
|------|------|
| 1. Struktura dat v AT | ✅ hotová |
| 1b. Heureka kategorizace | ✅ zapsaná v AT (142/143) |
| 2. Doplnění cen + dalších údajů | ⏳ čeká na výrobce |
| 3. Generátor feedu | ✅ multi-profile knihovna + 2 default profily, end-to-end ověřeno |
| 4. Hosting + auto-refresh | ✅ GH Action + Pages live |
| 5. Distribuce odběratelům | ✅ docs/feeds_for_partners.md, AT Automation čeká na napojení |
