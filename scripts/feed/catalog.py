"""
Načtení katalogu produktů z Airtable a interní model.

ProductCatalog drží všechny záznamy z Produkty_v2. Každý profil pak nad ním
běží svůj filter + render. AT je read-only ve směru ven (read records,
patch back jen do Feed_profile_index).
"""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent
ENV_PATH = ROOT / '.env'

# Pole, která se NIKDY nesmějí dostat do žádného feedu, bez ohledu na profil.
# Příklady (až budou citlivá pole zavedena):
#     "Marže",
#     "Konkurenční cena",
#     "Interní poznámka",
# Pokud profil omylem zařadí takové pole jako tag source, generátor failne
# v rendereru (viz renderer.py).
INTERNAL_FIELDS_BLOCKLIST: set[str] = set()


@dataclass
class Product:
    """Bohatý interní model produktu — drží všechna AT pole jako dict."""
    record_id: str
    fields: dict[str, Any] = field(default_factory=dict)

    def get(self, name: str, default: Any = None) -> Any:
        return self.fields.get(name, default)

    def has(self, name: str) -> bool:
        v = self.fields.get(name)
        if v is None:
            return False
        if isinstance(v, str) and not v.strip():
            return False
        if isinstance(v, list) and len(v) == 0:
            return False
        return True


@dataclass
class ProductCatalog:
    products: list[Product]
    fetched_at: str  # ISO timestamp

    def __len__(self) -> int:
        return len(self.products)

    def __iter__(self):
        return iter(self.products)


def load_env(env_path: Path = ENV_PATH) -> dict[str, str]:
    """Načte .env do dictu. Akceptuje formát KEY=VALUE  # comment."""
    env: dict[str, str] = {}
    with env_path.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            env[k.strip()] = v.split('  ')[0].strip()
    return env


def _airtable_paginate(token: str, base: str, table: str) -> list[dict]:
    """Vrátí všechny záznamy z tabulky, bez ohledu na velikost."""
    records: list[dict] = []
    offset: str | None = None
    while True:
        params: list[tuple[str, str]] = [('pageSize', '100')]
        if offset:
            params.append(('offset', offset))
        url = (
            f'https://api.airtable.com/v0/{base}/{urllib.parse.quote(table)}'
            f'?{urllib.parse.urlencode(params)}'
        )
        req = urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        records.extend(data.get('records', []))
        offset = data.get('offset')
        if not offset:
            break
    return records


def fetch_catalog(env: dict[str, str] | None = None) -> ProductCatalog:
    """Načte všech 143 produktů z Produkty_v2."""
    from datetime import datetime, timezone
    if env is None:
        env = load_env()
    raw = _airtable_paginate(
        token=env['AIRTABLE_TOKEN'],
        base=env['AIRTABLE_BASE_ID'],
        table=env['AIRTABLE_TABLE_NAME'],
    )
    products = [Product(record_id=r['id'], fields=r.get('fields', {})) for r in raw]
    return ProductCatalog(
        products=products,
        fetched_at=datetime.now(timezone.utc).isoformat(timespec='seconds'),
    )
