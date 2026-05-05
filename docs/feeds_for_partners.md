# Sidolux/Lakma — produktové feedy pro odběratele

Drogerie ZDE (distribuce produktů Lakma řady Sidolux v ČR a SR) poskytuje
B2B partnerům strukturovaný produktový feed. Účelem je usnadnit programatické
zalistování zboží do vašich systémů — místo ručního zadávání 140+ SKU
stáhnete vždy aktuální XML, ze kterého si svými skripty vyberete, co
potřebujete.

## Aktuální feedy

Rozcestník: <https://martin87pokorny.github.io/produktovy-feed-sidolux/>

| Feed | URL |
|------|-----|
| Heureka XML — verze CZ | <https://martin87pokorny.github.io/produktovy-feed-sidolux/heureka_general_cz.xml> |
| Heureka XML — verze SK | <https://martin87pokorny.github.io/produktovy-feed-sidolux/heureka_general_sk.xml> |

URL jsou stabilní, můžete je natvrdo zadat do vašeho stahovače.

## Formát

XML odpovídá specifikaci [Heureka XML Feed](https://sluzby.heureka.cz/napoveda/xml-feed/).
Struktura:

```xml
<SHOP>
  <SHOPITEM>
    <ITEM_ID>1010101</ITEM_ID>
    <PRODUCTNAME>...</PRODUCTNAME>
    <URL>https://www.sidolux.cz/cs-cz/produkty/...</URL>
    <PRICE_VAT>79.90</PRICE_VAT>
    <VAT>21%</VAT>
    <CATEGORYTEXT>Heureka.cz | Drogerie | ...</CATEGORYTEXT>
    <DESCRIPTION><![CDATA[...]]></DESCRIPTION>
    <EAN>5900536001234</EAN>
    <MANUFACTURER>Lakma</MANUFACTURER>
    <ITEMGROUP_ID>sidolux-universal-1000ml</ITEMGROUP_ID>
    <DELIVERY_DATE>0</DELIVERY_DATE>
    <IMGURL>...</IMGURL>
    <IMGURL_ALTERNATIVE>...</IMGURL_ALTERNATIVE>
    <PARAM><PARAM_NAME>Vůně</PARAM_NAME><VAL>...</VAL></PARAM>
    ...
  </SHOPITEM>
</SHOP>
```

### Klíčové údaje

| Tag | Vysvětlení |
|-----|------------|
| `ITEM_ID` | Kód Lakma — globálně unikátní identifikátor produktu, stabilní mezi běhy |
| `PRICE_VAT` | Doporučená maloobchodní cena s DPH (CZK pro CZ feed, EUR pro SK feed). Není to závazná velkoobchodní cena. |
| `URL` | Odkaz na produktovou stránku na sidolux.cz |
| `EAN` | Kus EAN — 8/12/13/14 číslic |
| `ITEMGROUP_ID` | Skupinuje varianty (např. všechny vůně Sidolux Universal 1000 ml). Produkty se stejným `ITEMGROUP_ID` patří k sobě. |
| `CATEGORYTEXT` | Plná cesta v Heureka taxonomii (CZ pro CZ feed, SK pro SK feed) |
| `MANUFACTURER` | Vždy `Lakma` |
| `IMGURL` | Hlavní fotka produktu |
| `IMGURL_ALTERNATIVE` | Další fotky (může být víc) |
| `PARAM` | Atributy produktu (Vůně, Objem, Vhodné povrchy, Hlavní technologie) |

`<DELIVERY>` blok feed neobsahuje — Sidolux není e-shop, dopravu si řeší
odběratel ve svém systému (paletová přeprava z centrálního skladu, přímá
dohoda s Drogerie ZDE).

## Aktualizace

- Feed se regeneruje automaticky **každé 4 hodiny** z dat v Airtable
- On-demand regeneraci může spustit interní tým (manuálně, garantovaně do 2 minut)
- Sortiment se reálně mění zpravidla 1× za kvartál; přesto doporučujeme
  stahovat alespoň 1× denně, abyste zachytili změny cen, popisů nebo nové vůně

Frekvenci stahování si nastavte ve svém systému. URL vrací HTTP 200 + XML
nebo HTTP 404 (pokud feed nebyl ještě nikdy vygenerován).

## Filtrace produktů

Ve feedu se objevují pouze produkty, které mají všechno z:
- `Přidat do feedu = Ano`
- vyplněnou cenu (CZK pro CZ feed, EUR pro SK feed)
- vyplněnou Heureka kategorii
- vyplněnou produktovou URL
- platný EAN

Produkty bez některé z položek se vynechávají. Nekompletní záznam ve feedu
neuvidíte — důvod může být dočasný (čekáme na ceník) nebo trvalý (produkt
nemá přidělenou Heureka kategorii).

## Custom feed pro váš systém

Pokud váš systém vyžaduje:
- jiné názvy XML tagů,
- doplňující údaje, které default Heureka schema neobsahuje (např. `MPN`, `Záruka`, vlastní kód),
- jinou taxonomii kategorií,
- jiný subset produktů (např. jen řadu PERLUX nebo jen 1L balení),

dejte vědět na e-mail níže. Vytvoříme samostatný profil s vašimi pravidly,
hostovaný na nové URL. Reference v rámci jednoho dotazu obvykle do týdne.

## Kontakt

| Co | Kdo / Kam |
|----|-----------|
| Obsah feedu, ceny, sortiment | Honza Pokorný — <honza@drogeriezde.cz> |
| Technická integrace, custom feed | Martin Pokorný — <martin@gby.agency> |

## Změny

| Datum | Co se stalo |
|-------|-------------|
| 2026-05-06 | Feed spuštěn v testovacím režimu (1 produkt jako sample) |
