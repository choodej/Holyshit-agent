"""Readable, collision-resistant ids + slug helper. Shared by all organs."""
from __future__ import annotations

import re
import secrets

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(text: str) -> str:
    return _SLUG_RE.sub("-", text.strip().lower()).strip("-")


def new_id(prefix: str) -> str:
    """e.g. new_id('mbr') -> 'mbr_8f3a2c1d'"""
    return f"{prefix}_{secrets.token_hex(4)}"
