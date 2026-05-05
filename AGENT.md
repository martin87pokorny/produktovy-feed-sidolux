# AGENT.md — pravidla pro AI agenty v projektu Produktový feed

Tento soubor je kontrakt pro libovolného AI agenta (Claude Code, Codex, Cursor, …), který v tomto projektu provádí změny. Před první akcí si přečti README.md a `docs/plan_feed.md`.

---

## Scope projektu

**Dělá:**
- Generuje XML produktový feed pro Heureka.cz a Heureka.sk
- Doplňuje a importuje feed-relevantní data do Airtable (Produkty_v2)
- Komunikuje s výrobcem přes Excel (`data/exchange/`)

**Nedělá:**
- Negeneruje produktové popisy (`Popis_draft`, `Benefity_draft`, …) — to řeší sourozenecký projekt `../Popisy_Produkty_Sidolux/`
- Neupravuje schválené Web pole (`Web popis CZ`, `Web benefity CZ`, …) — feed je čte read-only
- Neřeší Airtable Automation pro promote draftů — to je v sourozeneckém projektu
- Negeneruje fotky ani je nenahrává — Foto URL bude z Webflow CDN, řeší to web tým

---

## Single source of truth

**Airtable base `appSIEtMDgBsBPpjS`, tabulka `Produkty_v2`** je zdroj pravdy pro:
- 143 SKU řady Sidolux
- Identifikační údaje (Kód Lakma, EAN, Web slug, URL produktu CZ/SK)
- Schválené texty (Web popis/benefity/tipy/krátký popis CZ + SK) — _read-only_
- Cenové údaje (Cena CZK doporučená, Cena EUR doporučená) — vyplňuje výrobce
- Heureka kategorie CZ + SK
- Itemgroup ID (skupinování variant)
- Filtr `Přidat do feedu` (Ano/Ne) — Honza ručně přepíná

**Výstup feedu** je deterministicky odvozený z Airtable + statického configu (manufacturer="Lakma", delivery rules, atd.). **Nikdy neukládej business logiku do skriptů** — vše je v Airtable.

---

## Pravidla úprav

1. **Žádný PATCH bez `--dry-run` první**. Skript, který modifikuje Airtable, musí mít `--dry-run` přepínač a default je dry-run = OFF — uživatel ho musí explicitně pustit naostro.
2. **Nepřepisuj vyplněná Web pole** (Web popis, Web benefity, ...). Tato data spravuje sourozenecký projekt + Airtable Automation.
3. **Validuj povinná pole před zápisem do feedu**. Heureka tag PRICE_VAT, ITEM_ID, PRODUCTNAME, URL jsou povinné. Bez nich produkt vynech a logni `data/output/feed_warnings_*.log`.
4. **Filtruj feed podle `Přidat do feedu = "Ano"`**. To je jediný zdroj pravdy o tom, co publikovat. NEFILTRUJ podle Stav produktu, Web stav, atd.
5. **Slug formát**: spojení čísla a jednotky bez pomlčky (`500ml`, `30ks`, `40x40cm`). Regex `(\d+)\s+(ml|l|ks|cm|g|kg)\b` → `\1\2` před slugify.
6. **URL formát**:
   - CZ: `https://www.sidolux.cz/cs-cz/produkty/{slug}`
   - SK: `https://www.sidolux.cz/sk-sk/produkty/{slug}`
7. **DPH defaulty**: CZ 21 %, SK 23 %. Výrobce může v Excelu přepsat.

---

## Skripty — kontrakt

Každý skript v `scripts/`:
- Má docstring s popisem účelu, vstupů a výstupů
- Načítá `.env` z root projektu (cesta: `Path(__file__).resolve().parent.parent / '.env'`)
- Čte data z Airtable, produkuje JSON / XML / Excel artefakty do `data/`
- **Nemodifikuje vyplněná Web pole**
- Loguje do stdout v UTF-8 (`sys.stdout.reconfigure(encoding='utf-8')` na Windows)
- Pokud modifikuje Airtable, podporuje `--dry-run`

Pojmenování:
- `scripts/<sloveso>_<objekt>.py` (např. `generate_heureka_feed.py`, `import_pricing.py`, `validate_feed.py`)

---

## Závislosti / runtime

- **Python 3.13+** (testováno na 3.13 / Windows 11)
- **openpyxl 3.1+** pro Excel
- Vše ostatní z stdlib — preferuj `urllib` před `requests`, není potřeba `pip install`
- Žádný `anthropic` SDK — LLM práci dělá uživatel přímo přes Claude Code subscription

---

## Pracovní postup

1. **Začni `docs/plan_feed.md`** — kde jsme, co chybí
2. **Při změnách v Airtable** první vždy `--dry-run`, pak naostro
3. **Po každé větší změně** aktualizuj `memory/MEMORY.md` jednou větou (datum + co se stalo)
4. **Při generování feedu** vždy validuj proti https://sluzby.heureka.cz/napoveda/xml-feed/

---

## Když se zasekneš

- **Chybí přístup**: zkontroluj `.env` (token expiroval? Honza dokáže obnovit v Airtable Builder Hub)
- **Nesedí mapování pole**: ověř schémata přes `meta API` (`/v0/meta/bases/<base>/tables`)
- **Heureka odmítla feed**: spusť validátor https://sluzby.heureka.cz/sluzby/feed-validator/, log do `data/output/`

---

## Co _nikdy_ nedělej

- Negeneruj feed s prázdnými povinnými poli (PRICE_VAT, ITEM_ID, PRODUCTNAME, URL)
- Neukládej hesla/tokeny do skriptů ani repo
- Nepřepiš `Přidat do feedu` automaticky — ručně to přepíná Honza
- Negeneruj produktové texty (popisy, benefity, tipy) — to dělá sourozenecký projekt
- Nepush do prod hostingu bez `--dry-run` validace XML
