"""Adapter (ออปชัน): ส่ง "สรุป/ผลงาน" ไป ClickUp — ไม่ใช่ที่เก็บ log ดิบ

เหตุผล: ClickUp/Sheet ช้าและโดน rate-limit ถ้ายัด log ทุกบรรทัดระบบจะหน่วง
จึงส่งเฉพาะเหตุการณ์สำคัญ (เช่น สมาชิกใหม่) เป็น "ป้ายรายงาน"

ตัวนี้เป็น decorator: ห่อ Logger อีกตัว แล้วส่งต่อเฉพาะ event ใน whitelist
**การ POST ขึ้น ClickUp คือ external write** จึงต้องผ่าน SafetyGate (กฎข้อ 7):
default = DryRunGate -> preview แล้วไม่ยิงจริง (slice วิ่งได้ ไม่มีการเขียนนอกแบบเงียบๆ)
ใส่ AutoApproveGate / PolicyGate เมื่อพร้อมยิงของจริง โดยไม่ต้องแตะ domain
"""
from __future__ import annotations

from shared.safety import (
    DryRunGate,
    ExternalWriteAdapter,
    SafetyGate,
    WriteIntent,
)

from ..ports.logger import Logger

# เฉพาะเหตุการณ์ที่ "ควรขึ้นป้ายรายงาน" เท่านั้น
_REPORTABLE = {"register.created"}


class ClickUpReportingLogger(Logger, ExternalWriteAdapter):
    def __init__(self, inner: Logger, token: str | None = None,
                 list_id: str | None = None, gate: SafetyGate | None = None) -> None:
        # external write ต้องมี gate เสมอ; default เป็น dry-run (ปลอดภัยสุด)
        ExternalWriteAdapter.__init__(self, gate or DryRunGate())
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

        intent = WriteIntent(
            action="clickup.create_task",
            target=f"list/{self._list_id}",
            payload={"event": event, **fields},
            reversible=False,            # task ที่สร้างบน ClickUp ลบเองไม่ได้ง่ายๆ
        )
        result = self.guarded(intent, lambda: self._post(intent))
        if not result.ok:
            # ไม่อนุมัติ -> ไม่ยิง และบันทึกไว้ใน log จริงว่า defer (ใช้ contract เดิม)
            self._inner.emit("register.report_deferred",
                             deferred_event=event, reason=result.reason)

    def _post(self, intent: WriteIntent) -> str:
        # TODO: POST ไป ClickUp API จริง (เสียบทีหลังโดยไม่แตะ domain)
        # requests.post(f"https://api.clickup.com/api/v2/list/{self._list_id}/task", ...)
        return "posted"
