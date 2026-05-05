"""
Vytvoří jednoduchý HTML rozcestník nad feed_index.json pro odběratele.

Použití:
    python scripts/_build_feed_index_html.py <feed_index.json> <out.html>
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

if len(sys.argv) < 3:
    print("Usage: build_feed_index_html.py <feed_index.json> <out.html>", file=sys.stderr)
    sys.exit(2)

idx_path = Path(sys.argv[1])
out_path = Path(sys.argv[2])

if not idx_path.exists():
    # No feeds yet — write empty placeholder
    out_path.write_text(
        '<!doctype html><meta charset="utf-8"><title>Sidolux feeds</title>'
        '<h1>Sidolux/Lakma produktové feedy</h1><p>Žádné feedy zatím nebyly vygenerovány.</p>',
        encoding='utf-8'
    )
    sys.exit(0)

idx = json.loads(idx_path.read_text(encoding='utf-8'))
generated = idx.get('generated_at', '')
feeds = idx.get('feeds', [])

rows = []
for f in feeds:
    rows.append(
        f'<tr><td><code>{f["profile"]}</code></td>'
        f'<td><a href="{f["output_filename"]}">{f["output_filename"]}</a></td>'
        f'<td>{f["count"]}</td>'
        f'<td>{f["status"]}</td></tr>'
    )

html = f'''<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8">
<title>Sidolux/Lakma — produktové feedy</title>
<style>
  body {{ font-family: system-ui, sans-serif; max-width: 960px; margin: 2rem auto; padding: 0 1rem; }}
  table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; }}
  th, td {{ text-align: left; padding: 0.5rem; border-bottom: 1px solid #ddd; }}
  th {{ background: #f5f5f5; }}
  code {{ background: #f0f0f0; padding: 0.1rem 0.3rem; border-radius: 3px; }}
  .meta {{ color: #666; font-size: 0.9rem; }}
</style>
</head>
<body>
  <h1>Sidolux/Lakma — produktové feedy</h1>
  <p class="meta">Naposledy generováno: {generated}</p>
  <p>Tyto feedy slouží odběratelům k programatickému zalistování produktů.
     Formát XML odpovídá <a href="https://sluzby.heureka.cz/napoveda/xml-feed/">Heureka XML Feed</a> specifikaci
     (případně rozšířené o klientsky specifická pole).</p>
  <table>
    <thead><tr><th>Profil</th><th>Soubor</th><th>Počet produktů</th><th>Status</th></tr></thead>
    <tbody>
      {chr(10).join(rows)}
    </tbody>
  </table>
  <p class="meta">Provozuje <a href="https://drogeriezde.cz">Drogerie ZDE</a> · kontakt: honza@drogeriezde.cz</p>
</body>
</html>
'''

out_path.write_text(html, encoding='utf-8')
print(f'Wrote {out_path}')
