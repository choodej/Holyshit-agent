"""Port: ที่เก็บสมาชิก (domain ต้องการแค่ interface นี้ ไม่สนว่าเบื้องหลังเป็นอะไร)"""
from __future__ import annotations

from abc import abstractmethod

from shared.ports import Port

from ..domain.member import Member


class MemberRepository(Port):
    @property
    def port_name(self) -> str:
        return "MemberRepository"

    @abstractmethod
    def exists_id(self, member_id: str) -> bool: ...

    @abstractmethod
    def exists_username(self, username: str) -> bool: ...

    @abstractmethod
    def save(self, member: Member) -> None: ...

    @abstractmethod
    def get(self, member_id: str) -> Member | None: ...
