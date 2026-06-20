"""Port: ช่องทางรับคำสั่งเข้า (Telegram / CLI / อื่นๆ)

domain ไม่รู้จัก Telegram โดยตรง — มันรู้แค่ว่ามี "คำสั่งสมัคร" เข้ามา
adapter ฝั่ง inbound ทำหน้าที่แปลงข้อความช่องทางต่างๆ ให้เป็น RegisterCommand
"""
from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from typing import Callable

from shared.ports import Port


@dataclass(frozen=True)
class RegisterCommand:
    username: str
    source: str


class Inbound(Port):
    @property
    def port_name(self) -> str:
        return "Inbound"

    @abstractmethod
    def run(self, handle: Callable[[RegisterCommand], str]) -> None:
        """เริ่มรับคำสั่ง; เรียก handle() ต่อหนึ่งคำสั่ง และส่งข้อความตอบกลับผู้ใช้"""
        ...
