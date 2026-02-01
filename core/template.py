"""
Template utilities for SimpleChat.

Currently provides a lightweight Mustache-style replacement:
  - Replace {{ key }} with vars[key] (stringified).
  - Unmatched placeholders are left as-is by default (easier debugging).
"""

from __future__ import annotations

import re
from typing import Any, Mapping


_MUSTACHE_RE = re.compile(r"\{\{\s*([^\{\}\n]+?)\s*\}\}")


def render_mustache(text: str, vars: Mapping[str, Any] | None, *, keep_unmatched: bool = True) -> str:
    """
    Render {{var}} placeholders in text using vars mapping.

    Args:
        text: Input text (any string field).
        vars: Mapping of variable name -> value. Values will be stringified.
        keep_unmatched: If True, keep unknown placeholders like {{foo}} unchanged.
    """
    if not isinstance(text, str) or not text:
        return text

    # Fast path: avoid regex unless needed
    if "{{" not in text or "}}" not in text:
        return text

    if not vars or not isinstance(vars, Mapping):
        return text

    def _repl(match: re.Match) -> str:
        key = match.group(1).strip()
        if not key:
            return match.group(0) if keep_unmatched else ""
        if key in vars:
            value = vars.get(key)
            return "" if value is None else str(value)
        return match.group(0) if keep_unmatched else ""

    return _MUSTACHE_RE.sub(_repl, text)

