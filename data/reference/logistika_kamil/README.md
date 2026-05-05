# Logistická data Lakma – příprava pro XML feed

**Zdroj:** `logistická tabulka zboží LAKMA spotřební chemie 09042026.xlsx` (od výrobce, 9. 4. 2026)
**Extrahováno:** 2026-04-30
**Počet produktů:** 143

## Soubory

| Soubor | Použití |
|--------|---------|
| `logisticka_data_2026-04-09.json` | Strukturovaná data, primární zdroj pro skripty (XML feed generátor) |
| `logisticka_data_2026-04-09.csv` | Tabulkový pohled (UTF-8 s BOM, oddělovač `;`) – otevři v Excelu pro rychlou kontrolu |
| `README.md` | Tento soubor |

## Struktura JSON

```json
{
  "metadata": {
    "zdroj": "název souboru",
    "datum_zdroje": "2026-04-09",
    "datum_extrakce": "2026-04-30 ...",
    "pocet_produktu": 143,
    "sloupce_popis": { "klíč": "popis...", ... }
  },
  "produkty": [
    {
      "kod_lakma": "1010101",            // bez vedoucí 0 (konzistentní s Airtable)
      "kategorie_excel": "SIDOLUX EXPERT",  // sekce/řada z Excelu
      "kod_lakma_full": "01010101",       // s vedoucí 0 (původní formát výrobce)
      "kod_pl": "121-01-001-0014",
      "kod_celni": "3209100000",
      "ean_ks": 5902986200038,
      "ean_krt": 5902986201110,
      "nazev_zkraceny": "SDX EXP LESK PVC,LINOLEUM,DLAŽBA 750ml",
      "objem": "750ml",
      "zaruka_dny": 1080,
      "karton_ks": 10,                    // počet kusů v kartonu
      "vrstva_ks": 150,                   // počet kusů na vrstvě palety
      "vrstva_krt": 15,                   // počet kartonů na vrstvě palety
      "vrstva_pocet": 4,                  // počet vrstev na paletě
      "paleta_ks": 600,                   // počet kusů na celé paletě
      "paleta_krt": 60,                   // počet kartonů na celé paletě
      "hmotnost_vyrobek_kg": 0.83,        // hmotnost 1 ks
      "hmotnost_karton_kg": 8.3,          // hmotnost kartonu
      "hmotnost_paleta_kg": 498.0,        // hmotnost palety
      "rozmer_karton_delka_m": 0.26,      // rozměry kartonu v metrech
      "rozmer_karton_hloubka_m": 0.232,
      "rozmer_karton_vyska_m": 0.292,
      "vyrobek_delka_cm": 11.5,           // rozměry kusu v cm
      "vyrobek_hloubka_cm": 5.15,
      "vyrobek_vyska_cm": 27.0
    }
  ]
}
```

## Pokrytí dat (výsledky extrakce)

| Pole | Vyplněno |
|------|----------|
| Hmotnost výrobku, kartonu, palety | 143/143 ✓ |
| Počet kusů v kartonu / paletě | 143/143 ✓ |
| Rozměry kusu (délka × hloubka × výška) | 143/143 ✓ |
| Záruční lhůta (dny) | 137/143 |
| EAN KS | 138/143 (chybí u některých vzorků a B2B karton) |

## Použití pro XML feed

1. **Identifikační klíč:** `kod_lakma` (např. `1010101`) – odpovídá poli `Kód Lakma` v Airtable. Pomocí něj lze párovat logistická data s marketingovými popisy z Airtable (Popis_draft, Benefity_draft, Tipy_draft + jejich SK protějšky).

2. **Pro feed:**
   - Tělo produktu z Airtable (název, popis, benefity, tipy, fotky)
   - Logistická data odsud (váha, rozměry, EAN, balení, záruka)
   - Spojení přes `kod_lakma` jako primary key

3. **Příklad spojení v Pythonu:**
   ```python
   import json
   with open('new_data_kamil_lakma/logisticka_data_2026-04-09.json', 'r', encoding='utf-8') as f:
       log_data = {p['kod_lakma']: p for p in json.load(f)['produkty']}
   # pak při generování feedu:
   logistics = log_data.get(airtable_record['Kód Lakma'])
   ```

## Aktualizace dat

Pokud výrobce dodá novou verzi Excelu (např. `logistická tabulka ... 15052026.xlsx`):
1. Ulož ji do projektového rootu
2. Spusť extrakční skript (viz historie git nebo `_extract_logistics.py` ad-hoc)
3. Vznikne nový JSON/CSV s aktuálním datem v názvu
4. Smaž starý JSON/CSV po ověření, že nový soubor obsahuje vše potřebné

## Mapování `kategorie_excel` ⇄ Airtable řada

| Excel kategorie | Airtable `Web produktová řada CZ` |
|-----------------|-----------------------------------|
| SIDOLUX EXPERT | Sidolux EXPERT |
| SIDOLUX PREMIUM FLOOR CARE | Sidolux PREMIUM FLOOR CARE |
| SIDOLUX UNIVERSAL | Sidolux UNIVERSAL |
| SIDOLUX M péče o nábytku | Sidolux M péče o nábytek |
| SIDOLUX PROFFESIONAL | Sidolux PROFESSIONAL |
| SIDOLUX WINDOW | Sidolux WINDOW |
| PERLUX PRACÍ KAPSLE | PERLUX |
| SILUX WC | SILUX WC |
| SILUX HOUBIČKY | Silux |
| SILUX SPREJ | Silux |
| SILUX UNI VZORKY | Sidolux UNIVERSAL |
| PRIVÁTKA | (žádné mapování – privátní značky) |
| PENNY MIX 500ml | Sidolux UNIVERSAL |
| utěrka MIKROVLÁKNO | (žádné mapování – příslušenství) |
