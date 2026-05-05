"""
Feed generator library — multi-profile XML exporter z Airtable.

Public API:
    load_env, fetch_catalog, ProductCatalog, Product
    Profile, load_profile, list_profiles
    apply_filter
    render_xml
    validate_feed, FeedValidationError
"""
from .catalog import (
    Product,
    ProductCatalog,
    INTERNAL_FIELDS_BLOCKLIST,
    fetch_catalog,
    load_env,
)
from .profile import Profile, load_profile, list_profiles
from .filters import apply_filter
from .renderer import render_xml
from .validator import validate_feed, FeedValidationError

__all__ = [
    'Product', 'ProductCatalog', 'INTERNAL_FIELDS_BLOCKLIST',
    'fetch_catalog', 'load_env',
    'Profile', 'load_profile', 'list_profiles',
    'apply_filter',
    'render_xml',
    'validate_feed', 'FeedValidationError',
]
