"""Port: ตัวบันทึก log (เบื้องหลังเป็น JSONL local, หรือ ClickUp, หรืออื่นๆ)"""
from __future__ import annotations

from abc import abstractmethod

from shared.ports import Port


class Logger(Port):
    @property
    def port_name(self) -> str:
        return "Logger"

    @abstractmethod
    def emit(self, event: str, **fields) -> None:
        """บันทึกเหตุการณ์หนึ่งรายการ (event + ฟิลด์ประกอบ)"""
        ...
