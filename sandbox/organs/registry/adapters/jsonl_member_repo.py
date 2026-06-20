"""Adapter: เก็บสมาชิกเป็นไฟล์ JSONL (เร็ว ค้นได้ ไม่ต้องมี server)

หนึ่งบรรทัด = หนึ่งสมาชิก แก้/ซ่อมง่าย เปลี่ยนเป็น DB ทีหลังได้โดยไม่แตะ domain
"""
from __future__ import annotations

import json
from pathlib import Path

from ..domain.member import Member
from ..ports.member_repo import MemberRepository


class JsonlMemberRepository(MemberRepository):
    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._index: dict[str, Member] = {}
        self._usernames: set[str] = set()
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            return
        for line in self._path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            m = Member(**d)
            self._index[m.id] = m
            self._usernames.add(m.username.lower())

    def exists_id(self, member_id: str) -> bool:
        return member_id in self._index

    def exists_username(self, username: str) -> bool:
        return username.lower() in self._usernames

    def save(self, member: Member) -> None:
        with self._path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(member.to_dict(), ensure_ascii=False) + "\n")
        self._index[member.id] = member
        self._usernames.add(member.username.lower())

    def get(self, member_id: str) -> Member | None:
        return self._index.get(member_id)
