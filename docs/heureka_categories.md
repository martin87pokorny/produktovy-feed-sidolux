# Heureka kategorie CZ/SK

Tento workflow připravuje validní hodnoty `CATEGORYTEXT` pro pole Airtable:

- `Heureka kategorie CZ`
- `Heureka kategorie SK`

Do Airtable se tímto workflow nezapisuje nic automaticky. Výstupem je review Excel a import CSV. K 2026-05-05 je kategorizace připravená k nasazení do existujících polí Airtable `Heureka kategorie CZ` a `Heureka kategorie SK`.

## Zdroje

- CZ strom: `https://www.heureka.cz/direct/xml-export/shops/heureka-sekce.xml`
- SK strom: `https://www.heureka.sk/direct/xml-export/shops/heureka-sekce.xml`
- Lokální reference: `data/reference/heureka/`
- Mapování Sidolux: `config/heureka_category_mapping.json`

## Postup

1. Obnov oficiální strom kategorií:

   ```powershell
   python scripts\update_heureka_category_reference.py
   ```

2. Připrav review a import soubory z Airtable `Produkty_v2`:

   ```powershell
   python scripts\prepare_heureka_category_mapping.py
   ```

3. Zkontroluj review Excel:

   ```text
   data/heureka_categories/heureka_category_review_<date>.xlsx
   ```

4. Pro zápis do Airtable použij jen import CSV:

   ```text
   data/heureka_categories/heureka_category_import_<date>.csv
   ```

   CSV obsahuje pouze:

   ```text
   Kód Lakma
   Heureka kategorie CZ
   Heureka kategorie SK
   ```

## Aktuální výstup 2026-05-05

- Produkty v review: 143
- Vyřazeno: 1 (`1014009`, Q Power privátka)
- Validní návrhy CZ: 142
- Validní návrhy SK: 142
- Import CSV: 142 produktů
- Stav: připraveno k importu do Airtable, zatím nezapsáno

## Nasazení do Airtable

Pro import použij:

```text
data/heureka_categories/heureka_category_import_2026-05-05.csv
```

CSV je záměrně úzké a obsahuje jen:

```text
Kód Lakma
Heureka kategorie CZ
Heureka kategorie SK
```

Před importem zkontroluj review soubor:

```text
data/heureka_categories/heureka_category_review_2026-05-05.xlsx
```

Do AT nepřidávat žádná nová pomocná pole. Zapisovat pouze `Heureka kategorie CZ` a `Heureka kategorie SK`.

## Poznámky k mapování

Původní interní cesty typu `Drogerie | Úklid | Univerzální čističe` nejsou přesné podle aktuálního oficiálního XML Heureky. Nové návrhy používají plné publikované cesty, např.:

```text
Heureka.cz | Drogerie | Čisticí prostředky | Univerzální čisticí prostředky
Heureka.sk | Drogéria | Čistiace prostriedky | Univerzálne čistiace prostriedky
```

Tři produkty mají nižší jistotu, protože strom Heureky nemá přesnější drogerijní kategorii:

- `1011003` SIDOLUX duo na ošetření náhrobních kamenů
- `1011901` SIDOLUX Professional na ploché obrazovky a LCD
- `1011908` SIDOLUX Professional na silné nečistoty

Tyto položky jsou validní proti XML, ale stojí za ruční kontrolu před finálním importem.

## Navazující úkoly

- Ručně potvrdit tři low-confidence produkty `1011003`, `1011901`, `1011908`.
- Importovat `heureka_category_import_2026-05-05.csv` do Airtable `Produkty_v2`.
- Po importu upravit/ověřit feed generátor, aby `CATEGORYTEXT` bral přímo z polí `Heureka kategorie CZ/SK`.
- Po doplnění cen a Foto URL spustit finální validaci Heureka feedu.
