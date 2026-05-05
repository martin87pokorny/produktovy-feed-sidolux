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

# Inline SVG logo — když je SVG načteno přes <img>, nemá přístup k webfont
# parent dokumentu, takže <text> elementy fallbackují na sans-serif a glyph
# offsety v <tspan x="..."> se rozjedou. Inline SVG dědí Parkinsans z bodyho
# CSS a renderuje se správně.
ROOT = Path(__file__).resolve().parent.parent
LOGO_SVG_PATH = ROOT / 'data' / 'assets' / 'gby_logo_goodboys.svg'
logo_svg = ''
if LOGO_SVG_PATH.exists():
    raw = LOGO_SVG_PATH.read_text(encoding='utf-8')
    # Odstranit XML declaration, aby šel SVG inline-nout do HTML
    if raw.startswith('<?xml'):
        raw = raw.split('?>', 1)[1].lstrip()
    logo_svg = raw

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
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Parkinsans:wght@500;700;800&display=swap" rel="stylesheet">
<style>
  :root {{
    --navy: #201d48;
    --cream: #f3f2ed;
    --line: #d8d6cd;
    --muted: #6c6a82;
    --bg: #ffffff;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    font-family: "Parkinsans", ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
    font-weight: 500;
    color: var(--navy);
    background: var(--bg);
    max-width: 960px;
    margin: 0 auto;
    padding: 3rem 1.5rem 0;
    line-height: 1.55;
  }}
  h1 {{
    font-weight: 800;
    font-size: 2rem;
    margin: 0 0 0.35rem;
    letter-spacing: -0.015em;
    color: var(--navy);
  }}
  .meta {{ color: var(--muted); font-size: 0.875rem; margin: 0 0 2rem; }}
  p {{ margin: 0 0 1rem; }}
  a {{ color: var(--navy); text-decoration: underline; text-underline-offset: 3px; }}
  a:hover {{ text-decoration-thickness: 2px; }}
  table {{
    border-collapse: collapse;
    width: 100%;
    margin-top: 1.5rem;
    font-size: 0.9375rem;
  }}
  th, td {{
    text-align: left;
    padding: 0.75rem 0.6rem;
    border-bottom: 1px solid var(--line);
  }}
  th {{
    text-transform: uppercase;
    font-size: 0.7rem;
    letter-spacing: 0.12em;
    color: var(--muted);
    font-weight: 700;
    border-bottom: 1px solid var(--navy);
    background: var(--cream);
  }}
  td code {{
    font-family: ui-monospace, "JetBrains Mono", "Cascadia Code", Menlo, monospace;
    font-size: 0.875rem;
    background: var(--cream);
    padding: 0.15rem 0.45rem;
    border-radius: 4px;
    color: var(--navy);
  }}
  .footer {{
    margin: 5rem -1.5rem 0;
    padding: 2.5rem 1.5rem;
    background: var(--cream);
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 2rem;
    flex-wrap: wrap;
  }}
  .footer-brand {{
    display: inline-flex;
    align-items: center;
    text-decoration: none;
  }}
  .footer-brand svg {{
    height: 38px;
    width: auto;
    display: block;
  }}
  .footer-meta {{
    text-align: right;
    font-size: 0.875rem;
    color: var(--navy);
    line-height: 1.7;
  }}
  .footer-meta a {{ color: var(--navy); }}
  .footer-meta .label {{
    display: block;
    text-transform: uppercase;
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    color: var(--muted);
    font-weight: 700;
    margin-bottom: 0.15rem;
  }}
  @media (max-width: 540px) {{
    body {{ padding-top: 2rem; }}
    h1 {{ font-size: 1.625rem; }}
    .footer {{ flex-direction: column; align-items: flex-start; gap: 1.25rem; }}
    .footer-meta {{ text-align: left; }}
  }}
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

  <footer class="footer">
    <a class="footer-brand" href="https://gby.agency" aria-label="Good Boys Agency">
      {logo_svg}
    </a>
    <div class="footer-meta">
      <span class="label">Vytvořilo</span>
      <a href="https://gby.agency">gby.agency</a><br>
      <a href="mailto:martin@gby.agency">martin@gby.agency</a>
    </div>
  </footer>
</body>
</html>
'''

out_path.write_text(html, encoding='utf-8')
print(f'Wrote {out_path}')
