"""Member entity — OOP core บริสุทธิ์ (ไม่รู้จัก telegram/db/clickup)"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Member:
    id: str
    username: str
    source: str          # มาจากช่องทางไหน เช่น 'telegram', 'demo'
    created_at: str      # ISO8601

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "source": self.source,
            "created_at": self.created_at,
        }
