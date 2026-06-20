"""Adapter: ช่องทางจำลอง — ป้อนคำสั่งจากลิสต์ ใช้รัน slice/เดโม โดยไม่ต้องมี Telegram

พิสูจน์ว่า "เส้นเชื่อมต่อ" ทำงาน โดยไม่ผูกกับ token จริง
"""
from __future__ import annotations

from typing import Callable, Iterable

from ..ports.inbound import Inbound, RegisterCommand


class DemoInbound(Inbound):
    def __init__(self, usernames: Iterable[str]) -> None:
        self._usernames = list(usernames)

    def run(self, handle: Callable[[RegisterCommand], str]) -> None:
        for name in self._usernames:
            reply = handle(RegisterCommand(username=name, source="demo"))
            print(f"[demo] /register {name}  ->  {reply}")
