"""Adapter: log จริงเก็บ local เป็น JSONL (เร็ว ค้นย้อนหลังได้)

นี่คือ "สมุด log" ตัวจริง — ไม่ใช่ ClickUp
ClickUp ใช้แค่รับ "สรุป/ผลงาน" ผ่าน clickup_logger แยกต่างหาก
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from ..ports.logger import Logger


class JsonlLogger(Logger):
    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def emit(self, event: str, **fields) -> None:
        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "event": event,
            **fields,
        }
        with self._path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
