"""Shared utility for parsing stringified Python list columns safely.

Columns like genres, production_companies, production_countries, and cast
are serialized as stringified Python lists (e.g. "['Action', 'Drama']").
This module provides robust parsing with ast.literal_eval and fallbacks.
"""

import ast
import logging
from typing import Any, List

logger = logging.getLogger(__name__)


def parse_list_column(value: Any) -> List[str]:
    """Safely parse a string representation of a Python list into a list of strings.

    Args:
        value: Input value (stringified list, already parsed list, or NaN/None).

    Returns:
        List of cleaned string items. Returns an empty list if value is null,
        malformed, or empty.
    """
    if value is None:
        return []

    # If already a list or tuple
    if isinstance(value, (list, tuple)):
        return [str(x).strip() for x in value if str(x).strip()]

    # If not a string or empty string
    if not isinstance(value, str):
        return []

    val_str = value.strip()
    if not val_str or val_str in ("[]", "nan", "None"):
        return []

    try:
        parsed = ast.literal_eval(val_str)
        if isinstance(parsed, list):
            return [str(x).strip() for x in parsed if str(x).strip()]
        if isinstance(parsed, (set, tuple)):
            return [str(x).strip() for x in list(parsed) if str(x).strip()]
        return [str(parsed).strip()]
    except (ValueError, SyntaxError, MemoryError) as e:
        logger.debug("Failed to literal_eval value %r: %s", val_str[:50], e)
        # Fallback simple strip of brackets and split
        cleaned = val_str.strip("[]() ")
        if not cleaned:
            return []
        items = [part.strip().strip("'\"") for part in cleaned.split(",")]
        return [item for item in items if item]


def extract_primary_item(items: List[str], default: str = "Unknown") -> str:
    """Extract the first item from a list, or return a default value if empty."""
    if items and len(items) > 0:
        return items[0]
    return default
