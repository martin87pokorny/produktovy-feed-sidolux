"""
Post-render validace: XML well-formedness + sanity checks.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field


class FeedValidationError(Exception):
    pass


@dataclass
class ValidationReport:
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


_URL_RE = re.compile(r'^https://www\.sidolux\.cz/(cs-cz|sk-sk)/produkty/[a-z0-9-]+$')


def validate_feed(xml_bytes: bytes, *, item_element: str = 'SHOPITEM',
                  expect_min_items: int = 1) -> ValidationReport:
    report = ValidationReport(ok=True)

    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as e:
        report.ok = False
        report.errors.append(f'XML parse error: {e}')
        return report

    items = root.findall(f'.//{item_element}')
    if len(items) < expect_min_items:
        report.warnings.append(
            f'Feed obsahuje {len(items)} položek, čekáno >= {expect_min_items}'
        )

    seen_ids: set[str] = set()
    for it in items:
        item_id_el = it.find('ITEM_ID')
        item_id = item_id_el.text if item_id_el is not None else None
        if not item_id:
            report.errors.append('SHOPITEM bez ITEM_ID')
            continue
        if item_id in seen_ids:
            report.errors.append(f'Duplicitní ITEM_ID: {item_id}')
        seen_ids.add(item_id)

        url_el = it.find('URL')
        if url_el is not None and url_el.text:
            if not _URL_RE.match(url_el.text):
                report.warnings.append(f'{item_id}: URL nesplňuje pattern: {url_el.text}')

        ean_el = it.find('EAN')
        if ean_el is not None and ean_el.text:
            digits = ''.join(c for c in ean_el.text if c.isdigit())
            if len(digits) not in (8, 12, 13, 14):
                report.warnings.append(f'{item_id}: EAN má neobvyklou délku: {ean_el.text!r}')

    if report.errors:
        report.ok = False
    return report
