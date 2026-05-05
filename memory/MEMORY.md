# Project memory — Produktový feed

Krátký kontextový log pro Claude Code, ať při příští session nemusí dohledávat. **Zápisy jsou append-only**, nejnovější nahoře. Drž to do 200 řádků; starší věci přesunout do `archive_<rok>.md`.

---

## 2026-05-06 — Generátor end-to-end ověřený

- GH repo `martin87pokorny/produktovy-feed-sidolux` (public), GH Pages enabled na `gh-pages` branch.
- Workflow `Regenerate feeds` aktivní, manual run testovací produkt 5000013 prošel: 1 zařazen, validní XML pro CZ i SK na URL `https://martin87pokorny.github.io/produktovy-feed-sidolux/heureka_general_{cz,sk}.xml`. Patchback do AT `Feed_profile_index` přepsal status na OK.
- Node 20 deprecation eliminovaná `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true` env var.
- Drobné observace pro budoucí kroky:
  - `IMGURL` zatím neexistuje v AT jako stabilní pole — defaultně mapováno na `Foto 800×800` attachment URL (provisional). Po Webflow CDN integraci přemapovat.
  - SK profil přebírá hodnoty `PARAM` z CZ pole (`Vůně`, `Vhodné povrchy`, `Hlavní technologie`); pokud bude potřeba lokalizace hodnot pro SK odběratele, řešit přes nové AT pole nebo `value_map` v profilu.
- AT Automation tlačítko zatím není napojené (jen návod v `docs/at_automation_setup.md`).

## 2026-05-05 — Multi-profile feed generator postavený

- `scripts/feed/` knihovna: catalog, profile (extends), filters, transforms, renderer (CDATA, multi-IMGURL, PARAM), validator. Smoke test prošel.
- `scripts/generate_feeds.py` entry point — args `--profile <name>|all`, `--list-profiles`, `--validate-only`, `--public-url-base`, `--skip-patchback`.
- 2 default profily: `config/profiles/heureka_general_cz.json`, `heureka_general_sk.json`.
- AT struktura:
  - Pole `Feed profily` (multipleSelects) na `Produkty_v2`, `fldO4J5BZeby808uP`, choices: `heureka_general_cz`, `heureka_general_sk`. Prefilled u 141/141 aktivních produktů.
  - Tabulka `Feed_profile_index` (`tblehtW7zV3HZlzU4`): Profil, Aktivní, Output URL, Posl. regenerace, Počet produktů, Status posl. běhu, Posl. log, Poznámka. Generátor sem patchuje stav po každém běhu.
- `INTERNAL_FIELDS_BLOCKLIST` v `feed/catalog.py` připravený jako safety net (zatím prázdný).
- GH workflow `.github/workflows/regenerate_feeds.yml` (cron 4h + workflow_dispatch s `profile` input). Deploy přes peaceiris/actions-gh-pages na branch `gh-pages`.
- AT Automation návod v `docs/at_automation_setup.md` (fine-grained PAT s scope Actions write).
- **Blokuje:** vytvoření GH repa `martin87pokorny/produktovy-feed-sidolux` čeká na explicitní souhlas Honzy s veřejnou viditelností. Po vytvoření taky doplnit `workflow` scope k `gh` PAT a pushnout `.github/workflows/`.

## 2026-05-05 — Heureka kategorie zapsané do AT

- `scripts/import_heureka_categories.py` přepsal staré krátké cesty (`Drogerie | Úklid | …`) z `fill_feed_data.py` na nové plné cesty (`Heureka.cz | Drogerie | …`) z `heureka_category_import_2026-05-05.csv`.
- Pushed 142/142 (CZ i SK), verifikace 142/142 shoda. Q Power `1014009` zůstává bez kategorie (vyřazen).
- Pozn.: CSV má UTF-8 BOM, skript čte `utf-8-sig`. Šablona pro budoucí CSV importy.
- Low-confidence (`1011003`, `1011901`, `1011908`) zapsány s default návrhem „Univerzální čisticí prostředky"; Honza případně upraví ručně v AT.

## 2026-05-05 — Heureka kategorie ověřené proti oficiálnímu XML

- Přidán workflow `scripts/update_heureka_category_reference.py` + `scripts/prepare_heureka_category_mapping.py`; staženo 3683 CZ a 3531 SK kategorií z oficiálních XML exportů Heureky.
- Vygenerováno `data/heureka_categories/heureka_category_review_2026-05-05.xlsx` a import CSV pro 142 produktů; `1014009` Q Power privátka je z kategorizace vyřazená.
- Nové mapování používá plné validní cesty `Heureka.cz | ...` / `Heureka.sk | ...`; původní cesty `Drogerie | Úklid | ...` byly nahrazeny aktuálním stromem.
- Stav pro další session: kategorizace je připravená k nasazení do AT, zatím nezapsaná; importovat pouze existující pole `Heureka kategorie CZ` a `Heureka kategorie SK`.
- Před importem ručně zkontrolovat low-confidence produkty `1011003`, `1011901`, `1011908`.

## 2026-05-05 — projekt založen, Fáze 1 hotová

- Adresář `Produktovy_feed/` oddělen od `Popisy_Produkty_Sidolux/`
- Fáze 1 dokončena (struktura dat v Airtable):
  - 7 nových polí: Cena CZK/EUR doporučená, URL produktu CZ/SK, Itemgroup ID, Heureka kategorie CZ/SK
  - URL CZ formát: `https://www.sidolux.cz/cs-cz/produkty/{slug}`, SK: `https://www.sidolux.cz/sk-sk/produkty/{slug}`
  - Slug pravidlo: spojené číslo+jednotka (`500ml`), regex `(\d+)\s+(ml|l|ks|cm|g|kg)\b → \1\2`
  - Itemgroup ID: 117/143 (skupiny řada+objem ≥ 2 produktů)
  - Heureka kategorie: připravené k importu do AT pro 142 produktů; `1014009` Q POWER privátka je vyřazená
  - Pole `Přidat do feedu`: 141× Ano (V prodeji), 2× Ne (Doprodej, Ukončeno)
- Excel pro výrobce vygenerován: `data/exchange/cenik_pro_vyrobce_2026-05-05.xlsx`
  - 16 sloupců: Kód Lakma, Název, EAN, Řada, Objem, Cena bez DPH CZK, Sazba DPH CZ, Cena s DPH CZK (auto), 3× analogicky EUR, Země původu (prefilled "Polsko"), MPN, PAO, Záruka, Poznámka
  - DPH defaulty: CZ 21 %, SK 23 %
  - Cena s DPH se počítá Excel formulí

## Klíčové konstanty

- Airtable base: `appSIEtMDgBsBPpjS`
- Tabulka: `Produkty_v2` (id `tbl2TLtnbiqaBIRC2`)
- Počet produktů: 143
- Heureka feed spec: https://sluzby.heureka.cz/napoveda/xml-feed/

## Co je hotové (data v Airtable)

- ✅ 143/143: Kód Lakma, Web název CZ, Web název SK, Web slug, URL produktu CZ, URL produktu SK, EAN KS, EAN KRT (s `NA` pro 5 produktů bez kartonu/kódů), Web popis CZ, Web popis SK, Web benefity CZ/SK, Web tipy CZ/SK
- ✅ připraveno k importu: Heureka kategorie CZ, Heureka kategorie SK pro 142 produktů; `1014009` vyřazen
- ✅ 117/143: Itemgroup ID
- ⏳ 0/143: Cena CZK doporučená, Cena EUR doporučená — čeká se na výrobce
- ⏳ 0/143: Foto URL (Webflow CDN řeší web tým)
- ⏳ 0/143: MPN, Země původu, PAO, Záruka — výrobce vyplní v Excelu

## Důležitá pravidla práce

- LLM práce přes Claude Code subscription (žádné `anthropic` SDK)
- PATCH do Airtable přes `urllib`, batch po 10, default `--dry-run` pro destruktivní operace
- Slovenský jazyk přepisu = ne strojový překlad; mezinárodní vůně (Marseille soap, Lemongrass, Japanese cherry) zůstávají v původním tvaru
- Filtr feedu = pouze `Přidat do feedu = "Ano"` (jediný zdroj pravdy)
- **Tento projekt nemodifikuje Web pole / drafty** — to je v sourozeneckém `Popisy_Produkty_Sidolux`

## Otevřené otázky / blokátory

1. **Ceny od výrobce** (Excel) — bez nich nelze publikovat feed
2. **Webflow CDN** Foto URL — web tým musí publikovat fotky a vrátit URL pattern
3. **Heureka kategorie** — připravené k importu do AT; před zápisem zkontrolovat `1011003`, `1011901`, `1011908`
4. **Konfigurace dopravy** — DELIVERY_ID + ceny pro Heureka tag DELIVERY
