"""
Transformace hodnot z AT do tvaru pro XML feed.

Použití v profilu:
    {"tag": "DESCRIPTION", "source": "Web popis CZ", "transform": "html_to_plain"}
    {"tag": "PRICE_VAT", "source": "Cena CZK doporučená", "format": "decimal"}
"""
from __future__ import annotations

import re
from html.parser import HTMLParser
from typing import Any


class _PlainTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts: list[str] = []
        self._block_break_tags = {'p', 'br', 'li', 'div', 'h1', 'h2', 'h3', 'h4', 'tr'}

    def handle_starttag(self, tag, attrs):
        if tag in self._block_break_tags and self.parts and not self.parts[-1].endswith('\n'):
            self.parts.append('\n')

    def handle_endtag(self, tag):
        if tag in self._block_break_tags:
            self.parts.append('\n')

    def handle_data(self, data):
        self.parts.append(data)


def html_to_plain(value: Any) -> str:
    if not value:
        return ''
    p = _PlainTextExtractor()
    p.feed(str(value))
    text = ''.join(p.parts)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def to_decimal(value: Any) -> str:
    """Cena: AT vrací float, Heureka chce desetinné s tečkou bez tisícových oddělovačů."""
    if value is None or value == '':
        return ''
    try:
        return f'{float(value):.2f}'
    except (TypeError, ValueError):
        return ''


def to_percent(value: Any) -> str:
    """DPH: '21' nebo 21 -> '21'."""
    if value is None or value == '':
        return ''
    try:
        return str(int(round(float(value))))
    except (TypeError, ValueError):
        return ''


def first_attachment_url(value: Any) -> str:
    """AT multipleAttachments -> URL první přílohy. (Provisional, expirují.)"""
    if not value or not isinstance(value, list):
        return ''
    first = value[0]
    if isinstance(first, dict):
        return first.get('url', '') or ''
    return ''


def all_attachment_urls(value: Any) -> list[str]:
    """AT multipleAttachments -> seznam URL všech příloh."""
    if not value or not isinstance(value, list):
        return []
    return [a.get('url', '') for a in value if isinstance(a, dict) and a.get('url')]


def truncate(value: Any, max_len: int) -> str:
    s = str(value or '')
    if len(s) <= max_len:
        return s
    return s[: max_len - 1].rstrip() + '…'


_TRANSFORMS = {
    'html_to_plain': html_to_plain,
    'decimal': to_decimal,
    'percent': to_percent,
    'first_attachment_url': first_attachment_url,
    'all_attachment_urls': all_attachment_urls,
}


def apply_transform(name: str | None, value: Any) -> Any:
    if not name:
        return value
    fn = _TRANSFORMS.get(name)
    if fn is None:
        raise ValueError(f"Unknown transform: {name!r}")
    return fn(value)
