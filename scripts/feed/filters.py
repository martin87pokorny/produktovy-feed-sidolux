"""
Filter engine: vyhodnotí, jestli produkt patří do feedu daného profilu.

Filter spec (v profilu):
  filter:
    pridat_do_feedu: "Ano"           # rovnostní porovnání s 'Přidat do feedu'
    feed_profil_match: true           # produkt musí mít tento profil ve 'Feed profily'
    require_fields: [...]             # všechna jmenovaná pole musí být vyplněná
    extra_require_fields: [...]       # navíc k require_fields rodiče (extends-friendly)
    ean_must_be_valid: true           # EAN KS != "NA" a má 8/12/13/14 číslic
"""
from __future__ import annotations

from dataclasses import dataclass

from .catalog import Product


@dataclass
class FilterResult:
    included: bool
    reason: str = ''


def _is_valid_ean(value: str | None) -> bool:
    if not value or value.strip().upper() == 'NA':
        return False
    digits = ''.join(c for c in str(value) if c.isdigit())
    return len(digits) in (8, 12, 13, 14)


def apply_filter(product: Product, profile_name: str, filter_spec: dict) -> FilterResult:
    pridat = filter_spec.get('pridat_do_feedu')
    if pridat is not None:
        if product.get('Přidat do feedu') != pridat:
            return FilterResult(False, f"Přidat do feedu != {pridat!r}")

    if filter_spec.get('feed_profil_match', True):
        profily = product.get('Feed profily') or []
        if profile_name not in profily:
            return FilterResult(False, f"profil {profile_name!r} není ve 'Feed profily'")

    require_fields: list[str] = list(filter_spec.get('require_fields', []))
    require_fields.extend(filter_spec.get('extra_require_fields', []))
    for field_name in require_fields:
        if not product.has(field_name):
            return FilterResult(False, f"chybí pole {field_name!r}")

    if filter_spec.get('ean_must_be_valid'):
        if not _is_valid_ean(product.get('EAN KS')):
            return FilterResult(False, "neplatný EAN KS")

    return FilterResult(True, '')
