# CLAUDE.md

Pravidla a kontrakt pro Claude Code při práci v projektu Produktový feed.

## Začni zde
1. Přečti [`README.md`](README.md) — orientace v projektu, struktura
2. Přečti [`AGENT.md`](AGENT.md) — kontrakt pro AI (univerzální, platí i pro Claude)
3. Přečti [`docs/plan_feed.md`](docs/plan_feed.md) — aktuální stav
4. Zkontroluj [`memory/MEMORY.md`](memory/MEMORY.md) — kontextová paměť

## Specifika pro Claude Code

- **Jazyk komunikace**: čeština (se správnou diakritikou)
- **Auto mode**: Honza preferuje executive akci s minimem dotazů
- **Subscription**: LLM práce přes Claude Code subscription, ne Anthropic API. Žádné `anthropic` SDK do projektu.
- **Stylistika kódu**: stručné komentáře jen tam, kde je důvod neobvyklý. Žádné docstring romány.
- **Žádné emoji v souborech**, pokud to Honza výslovně nezmíní.

## Když Honza řekne …

| Honza řekne | Význam |
|-------------|--------|
| "vyplň/doplň pole v AT" | Přes Airtable REST API, batch po 10, default `--dry-run` |
| "udělej skript" | Python 3.13, `urllib` ne `requests`, do `scripts/` |
| "to dej do AT" | PATCH do `Produkty_v2`, nikdy nemodifikovat Web pole/drafty |
| "pošlu výrobci" | Excel přes openpyxl, do `data/exchange/` |
| "vygeneruj feed" | XML do `data/output/heureka_cz.xml` + `heureka_sk.xml`, validovat povinná pole |

## Sourozenecký projekt

`../Popisy_Produkty_Sidolux/` — generování produktových popisů. **Tyto dva projekty sdílí stejnou Airtable bázi**, ale mají různé scope:

- **Popisy** = drafty + Web pole (produktové texty)
- **Feed** = ceny, URL, kategorie, generátor XML (čte schválené texty read-only)

Pokud Honza zmíní popisy/drafty/promote, navigaj ho do `Popisy_Produkty_Sidolux`.

## Memory directory

Auto-memory pro tento projekt je v `memory/MEMORY.md` (lokální, projektově specifická). Globální user memory zůstává tam, kde je (Claude Code default).
