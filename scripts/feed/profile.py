"""
Loader feed profilů z config/profiles/*.json s podporou `extends`.

Profil je obyčejný JSON; `extends` ukazuje na jiný profil (bez .json), jehož
hodnoty se použijí jako základ. Override: `tags_add`, `tags_remove`, plus
shallow merge ostatních klíčů. Cyklus extends je zakázaný.
"""
from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent
PROFILES_DIR = ROOT / 'config' / 'profiles'


class ProfileError(Exception):
    pass


@dataclass
class Profile:
    name: str
    raw: dict[str, Any]

    @property
    def output_filename(self) -> str:
        return self.raw.get('output_filename', f'{self.name}.xml')

    @property
    def language(self) -> str:
        return self.raw.get('language', 'cz')

    @property
    def root_element(self) -> str:
        return self.raw.get('root_element', 'SHOP')

    @property
    def item_element(self) -> str:
        return self.raw.get('item_element', 'SHOPITEM')

    @property
    def filter(self) -> dict[str, Any]:
        return self.raw.get('filter', {})

    @property
    def tags(self) -> list[dict[str, Any]]:
        return self.raw.get('tags', [])

    @property
    def params(self) -> list[dict[str, Any]]:
        return self.raw.get('params', [])

    @property
    def delivery(self) -> list[dict[str, Any]]:
        return self.raw.get('delivery', [])

    @property
    def extras(self) -> list[dict[str, Any]]:
        return self.raw.get('extras', [])


def list_profiles(profiles_dir: Path = PROFILES_DIR) -> list[str]:
    if not profiles_dir.exists():
        return []
    return sorted(p.stem for p in profiles_dir.glob('*.json'))


def load_profile(name: str, profiles_dir: Path = PROFILES_DIR,
                 _seen: set[str] | None = None) -> Profile:
    """Načte profil včetně rekurzivního rozbalení `extends`."""
    if _seen is None:
        _seen = set()
    if name in _seen:
        raise ProfileError(f"Profile extends cycle: {' -> '.join(_seen)} -> {name}")
    _seen = _seen | {name}

    path = profiles_dir / f'{name}.json'
    if not path.exists():
        raise ProfileError(f"Profile '{name}' not found at {path}")

    with path.open('r', encoding='utf-8') as f:
        data = json.load(f)

    parent_name = data.get('extends')
    if parent_name:
        parent = load_profile(parent_name, profiles_dir=profiles_dir, _seen=_seen)
        merged = _merge_profile(deepcopy(parent.raw), data)
    else:
        merged = data

    merged['name'] = name
    return Profile(name=name, raw=merged)


def _merge_profile(parent: dict[str, Any], child: dict[str, Any]) -> dict[str, Any]:
    """
    Shallow merge s několika výjimkami:
      - tags: parent.tags + child.tags_add - child.tags_remove (po name)
      - params, delivery, extras: child override (pokud je v child, nahradí parent)
      - filter: shallow merge dictů
      - ostatní klíče: child override
    """
    out = deepcopy(parent)

    # tags
    parent_tags = list(parent.get('tags', []))
    if 'tags' in child:
        parent_tags = list(child['tags'])  # plný override
    if 'tags_remove' in child:
        remove = set(child['tags_remove'])
        parent_tags = [t for t in parent_tags if t.get('tag') not in remove]
    if 'tags_add' in child:
        parent_tags = parent_tags + list(child['tags_add'])
    out['tags'] = parent_tags

    # filter shallow merge
    if 'filter' in child:
        merged_filter = dict(parent.get('filter', {}))
        merged_filter.update(child['filter'])
        out['filter'] = merged_filter

    # ostatní klíče: child override
    for k, v in child.items():
        if k in ('tags', 'tags_add', 'tags_remove', 'filter', 'extends'):
            continue
        out[k] = deepcopy(v)

    return out
