"""สร้าง id ที่อ่านออก + ตรวจรูปแบบ ใช้ร่วมกันทุกอวัยวะ"""
from __future__ import annotations

import re
import secrets

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(text: str) -> str:
    return _SLUG_RE.sub("-", text.strip().lower()).strip("-")


def new_id(prefix: str) -> str:
    """เช่น new_id('mbr') -> 'mbr_8f3a2c1d'  (สั้น อ่านออก ชนกันยาก)"""
    return f"{prefix}_{secrets.token_hex(4)}"
