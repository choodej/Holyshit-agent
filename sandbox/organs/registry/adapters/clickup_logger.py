"""Adapter (ออปชัน): ส่ง "สรุป/ผลงาน" ไป ClickUp — ไม่ใช่ที่เก็บ log ดิบ

เหตุผล: ClickUp/Sheet ช้าและโดน rate-limit ถ้ายัด log ทุกบรรทัดระบบจะหน่วง
จึงส่งเฉพาะเหตุการณ์สำคัญ (เช่น สมาชิกใหม่) เป็น "ป้ายรายงาน"

ตัวนี้เป็น stub แบบ decorator: ห่อ Logger อีกตัว แล้วส่งต่อเฉพาะ event ที่อยู่ใน whitelist
ของจริงค่อยเสียบ HTTP client ภายหลัง โดยไม่ต้องแก้ domain
"""
from __future__ import annotations

from ..ports.logger import Logger

# เฉพาะเหตุการณ์ที่ "ควรขึ้นป้ายรายงาน" เท่านั้น
_REPORTABLE = {"register.created"}


class ClickUpReportingLogger(Logger):
    def __init__(self, inner: Logger, token: str | None = None,
                 list_id: str | None = None) -> None:
        self._inner = inner          # log จริงยังเขียนครบทุก event
        self._token = token
        self._list_id = list_id

    def emit(self, event: str, **fields) -> None:
        self._inner.emit(event, **fields)
        if event in _REPORTABLE:
            self._report(event, fields)

    def _report(self, event: str, fields: dict) -> None:
        if not (self._token and self._list_id):
            return  # ยังไม่ตั้งค่า -> ข้ามเงียบๆ (slice ยังวิ่งได้)
        # TODO: POST ไป ClickUp API (เสียบทีหลังโดยไม่แตะ domain)
        # requests.post(f"https://api.clickup.com/api/v2/list/{self._list_id}/task", ...)
