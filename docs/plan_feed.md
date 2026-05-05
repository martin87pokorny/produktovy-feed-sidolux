# Plán produktového feedu — Heureka.cz + Heureka.sk

> Stav k 2026-05-05. Aktualizuj při každém větším posunu.

## Cíl

Generovat XML feed pro **Heureka.cz** a **Heureka.sk** ze 143 produktů řady Sidolux. Klient (Lakma) není e-shop — ceny jsou pouze doporučené MOC pro porovnávač.

---

## Mapování Heureka tag → Airtable Produkty_v2

| Heureka tag | Povinné? | Airtable | Stav |
|-------------|----------|----------|------|
| ITEM_ID | ✓ | Kód Lakma | ✅ 143/143 |
| PRODUCTNAME | ✓ | Web název CZ / SK | ✅ 143/143 |
| URL | ✓ | URL produktu CZ / SK | ✅ 143/143 |
| PRICE_VAT | ✓ | Cena CZK doporučená / Cena EUR doporučená | ⏳ čeká na výrobce |
| DESCRIPTION | doporučeno | Web popis CZ / SK | ✅ |
| CATEGORYTEXT | doporučeno | Heureka kategorie CZ / SK | ✅ zapsáno v AT: 142/143, `1014009` vyřazen |
| IMGURL | doporučeno | Foto 800×800 → Webflow CDN | ⏳ Webflow CDN |
| IMGURL_ALTERNATIVE | volitelné | Galerie produktu → Webflow CDN | ⏳ |
| EAN | povinné pro chemii | EAN KS | ✅ (2× NA) |
| MANUFACTURER | doporučeno | konstanta `Lakma` (config) | ✅ |
| PRODUCTNO | volitelné | MPN / Kód výrobce (z Excelu) | ⏳ |
| PARAM | doporučeno | Vůně, Objem, Vhodné povrchy, Hlavní technologie | ✅ |
| ITEMGROUP_ID | doporučeno (varianty) | Itemgroup ID | ✅ 117/143 (zbylých 26 jsou solitéři) |
| DELIVERY_DATE | doporučeno | konstanta `0` (config) | ✅ |
| DELIVERY | doporučeno | konfig feed | ⏳ |
| VAT | volitelné | Sazba DPH CZ/SK (z Excelu) | ⏳ |

---

## Itemgroup ID pravidlo

`{slug-řady}-{objem}` — pro produkty kde se liší jen vůně. Např. všech 21 vůní `Sidolux Universal 1000ml` má hodnotu `sidolux-universal-1000ml`. Heureka pak nabízí selektor vůně na 1 produkt. stránce.

---

## Heureka kategorie — mapování řad (12 řad)

| Řada | CZ | SK |
|------|-----|-----|
| Sidolux UNIVERSAL | Heureka.cz \| Drogerie \| Čisticí prostředky \| Univerzální čisticí prostředky | Heureka.sk \| Drogéria \| Čistiace prostriedky \| Univerzálne čistiace prostriedky |
| Sidolux ECO | Heureka.cz \| Drogerie \| Ekologická domácnost \| Ekologické čisticí prostředky | Heureka.sk \| Drogéria \| Ekologická domácnosť \| Ekologické čistiace prostriedky |
| Sidolux EXPERT | Heureka.cz \| Drogerie \| Čisticí prostředky \| Leštící prostředky \| Leštidla na podlahy | Heureka.sk \| Drogéria \| Čistiace prostriedky \| Leštiace prostriedky \| Leštidlá na podlahy |
| Sidolux PREMIUM FLOOR CARE | Heureka.cz \| Drogerie \| Čisticí prostředky \| Čistící prostředky na podlahy | Heureka.sk \| Drogéria \| Čistiace prostriedky \| Čistiace prostriedky na podlahy |
| Sidolux WINDOW | Heureka.cz \| Drogerie \| Čisticí prostředky \| Čistící prostředky na okna a skla | Heureka.sk \| Drogéria \| Čistiace prostriedky \| Čistiace prostriedky na okná a sklá |
| Sidolux M péče o nábytek | Heureka.cz \| Drogerie \| Čisticí prostředky \| Leštící prostředky \| Leštidla na nábytek a přípravky proti prachu | Heureka.sk \| Drogéria \| Čistiace prostriedky \| Leštiace prostriedky \| Leštidlá na nábytok a prípravky proti prachu |
| Sidolux PROFESSIONAL | mix podle názvu: univerzální / koupelna+kuchyně / odpady / kamna+krby | mix podle názvu: univerzální / kúpeľne+kuchyne / odpady |
| Sidolux Praní + PERLUX | mix podle názvu: odstraňovače skvrn / prací gely / kapsle / aviváže / aditiva | mix podle názvu: odstraňovače škvŕn / pracie gély / kapsule / aviváže / aditíva |
| MR. TEPPICH | Heureka.cz \| Drogerie \| Čisticí prostředky \| Čisticí prostředky na koberce a čalounění | Heureka.sk \| Drogéria \| Čistiace prostriedky \| Čistiace prostriedky na koberce a čalúnenie |
| SILUX WC | Heureka.cz \| Drogerie \| Čisticí prostředky \| Dezinfekční prostředky na WC | Heureka.sk \| Drogéria \| Čistiace prostriedky \| Dezinfekčné prostriedky na WC |
| Silux | mix podle názvu: houbičky / utěrky / nábytek | mix podle názvu: hubky / utierky / nábytok |

Detailní mapování a generování review/import souborů: [`docs/heureka_categories.md`](heureka_categories.md).
Q Power `1014009` je z kategorizace vyřazený.

---

## Filtrování feedu

Generátor zařadí produkt do feedu právě tehdy, když:
- `Přidat do feedu` = `"Ano"` *(Honza ručně přepíná v Airtable)*
- AND `Cena CZK doporučená` (resp. `Cena EUR doporučená` pro SK feed) je vyplněná
- AND `Foto URL` je dostupné (po Webflow CDN integraci)
- AND `Heureka kategorie CZ` (resp. SK) je vyplněná

Produkty bez některého z těchto se vynechají + zaloguje varování do `data/output/feed_warnings_*.log`.

---

## Otevřené úkoly (Fáze 2)

| # | Úkol | Vlastník | Stav |
|---|------|---------|------|
| 1 | Vyplnit ceník (Excel pro výrobce) | výrobce / Lakma PL | odesláno 2026-05-05 |
| 2 | Importovat vyplněný ceník zpět do Airtable | feed projekt | po doručení |
| 3 | Importovat připravené Heureka kategorie do existujících polí AT | feed projekt | ✅ hotovo 2026-05-05 (142/142, `scripts/import_heureka_categories.py`) |
| 4 | Manuálně přiřadit Heureka kategorii pro 1014009 (Q POWER privátka) | — | zrušeno, produkt vyřazen z kategorizace |
| 5 | Webflow CDN integrace pro Foto URL | Honza + web tým | čeká |
| 6 | Konfigurace dopravy (DELIVERY_ID, DELIVERY_PRICE) | Honza | čeká |

---

## Handoff pro další session

- Heureka kategorizace zapsaná do AT (2026-05-05, 142/142).
- Generátor `scripts/generate_feeds.py` + `scripts/feed/` knihovna postavené, smoke test prošel.
- 2 default profily (`heureka_general_cz`, `heureka_general_sk`) v `config/profiles/`.
- AT připravena: `Feed profily` field + `Feed_profile_index` tabulka.
- Generátor patchuje stav do `Feed_profile_index` po každém běhu — prozatím status `Warning` (0 produktů), důvod chybí ceny.
- GH workflow `.github/workflows/regenerate_feeds.yml` připravený (cron 4h + workflow_dispatch).
- AT Automation návod v `docs/at_automation_setup.md`.

## Otevřené blokátory

1. **GitHub repo nezaložen** — čeká na explicitní souhlas Honzy s veřejnou viditelností. Po souhlasu: `gh repo create martin87pokorny/produktovy-feed-sidolux --public --source=. --remote=origin --push`.
2. **`gh` PAT chybí scope `workflow`** — bez toho nelze pushnout `.github/workflows/`. Refresh: `gh auth refresh -h github.com -s workflow`.
3. **GitHub Secrets** v repu po jeho vytvoření: `AIRTABLE_TOKEN`, `AIRTABLE_BASE_ID`, `AIRTABLE_TABLE_NAME`.
4. **GitHub Pages** zapnout v Settings → Pages → Source: `gh-pages` branch.
5. **Ceny od výrobce** + **Webflow CDN URL fotek** — bez nich proběhne feed s 0 produkty (status Warning), generátor je tomu připravený.
6. **AT Automation** s fine-grained PAT podle `docs/at_automation_setup.md`.

---

## Fáze 3 — Generátor

`scripts/generate_heureka_feed.py`:
- Vstup: Airtable + statický config (`config/feed_config.json`)
- Výstup: `data/output/heureka_cz.xml`, `data/output/heureka_sk.xml`
- Validace: povinná pole, EAN format, URL format
- Log: `data/output/feed_log_<timestamp>.txt`

Config struktura (návrh):
```json
{
  "manufacturer": "Lakma",
  "delivery_date_default": 0,
  "delivery": [
    {"id": "CESKA_POSTA", "price": 99},
    {"id": "ZASILKOVNA", "price": 79},
    {"id": "PPL", "price": 119}
  ],
  "heureka_cpc": null,
  "params_to_export": ["Vůně", "Objem", "Vhodné povrchy", "Hlavní technologie"]
}
```

---

## Fáze 4 — Hosting + auto-refresh

- Cron / GitHub Action na regeneraci každé 2-4 hodiny (Heureka zvládá tuto frekvenci na FREE režimu po 4 h, na PPC po 2 h)
- Hosting feedu: `https://www.sidolux.cz/feed/heureka_cz.xml` (vyžádá web tým)
- Validace přes Heureka feed-validator po každém deployi
- Monitoring: log alertů, kdy poslední úspěšná regenerace, kolik produktů ve feedu
