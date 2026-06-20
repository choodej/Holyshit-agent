"""Composition root ของอวัยวะ 'registry'

ที่เดียวที่ต่อสายทุกชิ้นเข้าด้วยกัน (domain + adapters)
domain ไม่รู้จัก adapter; adapter ไม่รู้จักกัน; มาเจอกันที่นี่เท่านั้น

รัน:
  python organs/registry/app.py --demo       # ไม่ต้องมี token
  python organs/registry/app.py --telegram   # ต้องตั้ง TELEGRAM_BOT_TOKEN
"""
from __future__ import annotations

import sys
from pathlib import Path

# ให้รันตรงๆ ได้ (เพิ่ม sandbox/ เข้า path เพื่อ import แบบ absolute)
_SANDBOX = Path(__file__).resolve().parents[2]
if str(_SANDBOX) not in sys.path:
    sys.path.insert(0, str(_SANDBOX))

from shared.result import Result  # noqa: E402

from organs.registry.adapters.clickup_logger import ClickUpReportingLogger  # noqa: E402
from organs.registry.adapters.demo_inbound import DemoInbound  # noqa: E402
from organs.registry.adapters.jsonl_logger import JsonlLogger  # noqa: E402
from organs.registry.adapters.jsonl_member_repo import JsonlMemberRepository  # noqa: E402
from organs.registry.adapters.telegram_inbound import TelegramInbound  # noqa: E402
from organs.registry.domain.registry_service import RegistryService  # noqa: E402
from organs.registry.ports.inbound import Inbound, RegisterCommand  # noqa: E402

_DATA = _SANDBOX / "organs" / "registry" / ".data"


def build_service() -> RegistryService:
    repo = JsonlMemberRepository(_DATA / "members.jsonl")
    base_logger = JsonlLogger(_DATA / "registry.log.jsonl")
    logger = ClickUpReportingLogger(base_logger)  # log จริง local + (ออปชัน) สรุปไป ClickUp
    return RegistryService(repo, logger)


def make_handler(service: RegistryService):
    def handle(cmd: RegisterCommand) -> str:
        result: Result = service.register(cmd.username, source=cmd.source)
        if result.ok:
            return f"✅ สมัครสำเร็จ id={result.value.id} username={result.value.username}"
        if result.needs_decision:
            lines = [f"❓ {result.question}"]
            for c in result.choices:
                mark = " ⭐(แนะนำ)" if c.recommended else ""
                lines.append(f"  - [{c.key}] {c.label}{mark}")
            return "\n".join(lines)
        return f"⛔ {result.reason}"

    return handle


def run(inbound: Inbound) -> None:
    service = build_service()
    inbound.run(make_handler(service))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "--demo"
    if mode == "--telegram":
        run(TelegramInbound())
    else:
        # เดโม: รวมเคสปกติ + ชื่อซ้ำ (ต้องถามก่อนสร้าง) + ชื่อผิดรูปแบบ
        run(DemoInbound(["alice", "alice", "x"]))
