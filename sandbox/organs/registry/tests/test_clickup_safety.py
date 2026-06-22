"""พิสูจน์ว่า external write (ClickUp) ผ่าน SafetyGate จริง — กฎข้อ 7

- default = DryRunGate -> ไม่ยิงจริง และบันทึก report_deferred
- AutoApproveGate -> ยิงจริง
- เทสนี้ทำให้ "กฎ" กับ "โค้ด" ตรงกัน ไม่ใช่แค่คำสัญญาใน README
"""
from __future__ import annotations

from shared.safety import AutoApproveGate, DryRunGate

from organs.registry.adapters.clickup_logger import ClickUpReportingLogger


class _CaptureLogger:
    """Logger ปลอมไว้เก็บ event ที่ inner ได้รับ (พิสูจน์ behavior)."""
    port_name = "Logger"

    def __init__(self) -> None:
        self.events: list[str] = []

    def emit(self, event: str, **fields) -> None:
        self.events.append(event)


def test_default_gate_is_dry_run_and_does_not_post():
    inner = _CaptureLogger()
    posted = []
    log = ClickUpReportingLogger(inner, token="t", list_id="L")
    log._post = lambda intent: posted.append(intent) or "posted"  # type: ignore

    log.emit("register.created", id="reg_1", label="alice")

    assert posted == []                                   # ไม่ยิงจริง
    assert "register.report_deferred" in inner.events     # บันทึกว่า defer


def test_approved_gate_posts():
    inner = _CaptureLogger()
    posted = []
    log = ClickUpReportingLogger(inner, token="t", list_id="L", gate=AutoApproveGate())
    log._post = lambda intent: posted.append(intent) or "posted"  # type: ignore

    log.emit("register.created", id="reg_1", label="alice")

    assert len(posted) == 1
    assert "register.report_deferred" not in inner.events


def test_non_reportable_event_never_touches_external():
    inner = _CaptureLogger()
    posted = []
    log = ClickUpReportingLogger(inner, token="t", list_id="L", gate=AutoApproveGate())
    log._post = lambda intent: posted.append(intent) or "posted"  # type: ignore

    log.emit("register.rejected", reason="invalid")       # ไม่อยู่ใน whitelist

    assert posted == []


def test_unconfigured_skips_quietly():
    """ไม่มี token/list -> slice ต้องวิ่งได้ ไม่ไปแตะ gate."""
    inner = _CaptureLogger()
    seen = []
    log = ClickUpReportingLogger(inner, gate=DryRunGate(sink=seen.append))
    log.emit("register.created", id="reg_1", label="alice")
    assert seen == []                                     # ไม่ preview เพราะยังไม่ตั้งค่า
