"""
XML renderer: produkt + profil -> XML element.

Tag spec (v profilu, list pod klíčem 'tags'):
  {"tag": "ITEM_ID", "source": "Kód Lakma", "required": true}
  {"tag": "PRICE_VAT", "source": "Cena CZK doporučená", "format": "decimal"}
  {"tag": "MANUFACTURER", "constant": "Lakma"}
  {"tag": "EAN", "source": "EAN KS", "skip_if": "NA"}
  {"tag": "DESCRIPTION", "source": "Web popis CZ", "transform": "html_to_plain", "wrap_cdata": true}
  {"tag": "IMGURL_ALTERNATIVE", "source": "Galerie produktu", "transform": "all_attachment_urls", "repeat": true}

Formaty (zkratka pro běžné transformy):
  'decimal' -> apply_transform('decimal')
  'percent' -> apply_transform('percent')

Constants jdou do tagu jako string. Source čte z product.fields.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Any

from .catalog import INTERNAL_FIELDS_BLOCKLIST, Product
from .profile import Profile
from .transforms import apply_transform


class FeedConfigError(Exception):
    pass


class FeedRenderError(Exception):
    pass


def _resolve_value(product: Product, tag_def: dict[str, Any]) -> Any:
    if 'constant' in tag_def:
        return tag_def['constant']

    source = tag_def.get('source')
    if source is None:
        return None

    if source in INTERNAL_FIELDS_BLOCKLIST:
        raise FeedConfigError(
            f"Tag {tag_def.get('tag')!r} odkazuje na zablokované pole "
            f"{source!r} (INTERNAL_FIELDS_BLOCKLIST)."
        )

    value = product.get(source)

    skip_if = tag_def.get('skip_if')
    if skip_if is not None and value is not None:
        if str(value).strip() == str(skip_if):
            return None

    transform = tag_def.get('transform')
    fmt = tag_def.get('format')
    if transform:
        value = apply_transform(transform, value)
    elif fmt in ('decimal', 'percent'):
        value = apply_transform(fmt, value)

    if value is None or value == '':
        if 'default' in tag_def:
            value = tag_def['default']

    return value


def _add_tag(parent: ET.Element, tag_name: str, value: Any, wrap_cdata: bool) -> None:
    el = ET.SubElement(parent, tag_name)
    text = '' if value is None else str(value)
    if wrap_cdata:
        # CDATA wrap přes vlastní ET hack
        el.text = f'__CDATA_OPEN__{text}__CDATA_CLOSE__'
    else:
        el.text = text


def render_product(product: Product, profile: Profile) -> tuple[ET.Element | None, list[str]]:
    """
    Vrátí (element, missing_required) nebo (None, missing) když chybí required.
    """
    item = ET.Element(profile.item_element)
    missing_required: list[str] = []

    for tag_def in profile.tags:
        tag_name = tag_def.get('tag')
        if not tag_name:
            raise FeedConfigError("Tag def missing 'tag' name in profile %s" % profile.name)
        try:
            value = _resolve_value(product, tag_def)
        except FeedConfigError:
            raise
        except Exception as e:
            raise FeedRenderError(
                f"Error resolving tag {tag_name!r} for product {product.get('Kód Lakma')!r}: {e}"
            ) from e

        is_empty = value is None or value == '' or value == []

        if is_empty:
            if tag_def.get('required'):
                missing_required.append(tag_name)
            continue

        wrap_cdata = bool(tag_def.get('wrap_cdata'))

        if tag_def.get('repeat') and isinstance(value, list):
            for v in value:
                _add_tag(item, tag_name, v, wrap_cdata)
        else:
            _add_tag(item, tag_name, value, wrap_cdata)

    # PARAM bloky
    for param_def in profile.params:
        param_name = param_def.get('name')
        source = param_def.get('source')
        if source in INTERNAL_FIELDS_BLOCKLIST:
            raise FeedConfigError(
                f"Param {param_name!r} odkazuje na zablokované pole {source!r}."
            )
        val = product.get(source)
        if val is None or val == '' or val == []:
            continue
        param_el = ET.SubElement(item, 'PARAM')
        ET.SubElement(param_el, 'PARAM_NAME').text = param_name
        ET.SubElement(param_el, 'VAL').text = str(val)

    # DELIVERY bloky (z configu profilu)
    for delivery in profile.delivery:
        d_el = ET.SubElement(item, 'DELIVERY')
        for k, v in delivery.items():
            ET.SubElement(d_el, k.upper()).text = str(v)

    # EXTRAS — volné dodatečné tagy z configu profilu (per-klient custom)
    for extra in profile.extras:
        tag_name = extra.get('tag')
        if not tag_name:
            continue
        try:
            value = _resolve_value(product, extra)
        except FeedConfigError:
            raise
        if value is None or value == '':
            continue
        _add_tag(item, tag_name, value, bool(extra.get('wrap_cdata')))

    if missing_required:
        return None, missing_required
    return item, []


def render_xml(products: list[Product], profile: Profile) -> tuple[bytes, dict]:
    """
    Vyrenderuje XML pro daný profil.
    Vrací (xml_bytes, stats) kde stats má 'included', 'skipped_missing_required',
    'skipped_reasons' (list[(kod, [missing])]).
    """
    root = ET.Element(profile.root_element)
    stats = {
        'included': 0,
        'skipped_missing_required': 0,
        'skipped_reasons': [],
    }

    for p in products:
        item, missing = render_product(p, profile)
        if item is None:
            stats['skipped_missing_required'] += 1
            stats['skipped_reasons'].append((p.get('Kód Lakma'), missing))
            continue
        root.append(item)
        stats['included'] += 1

    ET.indent(root, space='  ')
    xml_bytes = ET.tostring(root, encoding='utf-8', xml_declaration=True)

    # Post-process: nahradit CDATA placeholdery za <![CDATA[...]]>
    # ET.tostring escapuje speciální znaky, takže placeholder dostal zpracování.
    # Použijeme přímou náhradu na bytes.
    xml_text = xml_bytes.decode('utf-8')
    xml_text = xml_text.replace('__CDATA_OPEN__', '<![CDATA[').replace('__CDATA_CLOSE__', ']]>')

    return xml_text.encode('utf-8'), stats
