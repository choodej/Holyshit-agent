"""Composition root ของอวัยวะ 'registry'

ที่เดียวที่ต่อสายทุกชิ้นเข้าด้วยกัน (domain + adapters)
domain ไม่รู้จัก adapter; adapter ไม่รู้จักกัน; มาเจอกันที่นี่เท่านั้น

รัน:
  python organs/registry/app.py --demo       # ไม่ต้องมี token
  python organs/registry/app.py --telegram   # ต้องตั้ง TELEGRAM_BOT_TOKEN
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# ให้รันตรงๆ ได้ (เพิ่ม sandbox/ เข้า path เพื่อ import แบบ absolute)
_SANDBOX = Path(__file__).resolve().parents[2]
if str(_SANDBOX) not in sys.path:
    sys.path.insert(0, str(_SANDBOX))

from shared.result import Result  # noqa: E402
from tools.token_compressor import TokenCompressor, digest_events, stats  # noqa: E402

from organs.registry.adapters.clickup_logger import ClickUpReportingLogger  # noqa: E402
from organs.registry.adapters.demo_inbound import DemoInbound  # noqa: E402
from organs.registry.adapters.jsonl_logger import JsonlLogger  # noqa: E402
from organs.registry.adapters.jsonl_member_repo import JsonlMemberRepository  # noqa: E402
from organs.registry.adapters.telegram_inbound import TelegramInbound  # noqa: E402
from organs.registry.domain.registry_service import RegistryService  # noqa: E402
from organs.registry.ports.inbound import Inbound, RegisterCommand  # noqa: E402

_DATA = _SANDBOX / "organs" / "registry" / ".data"
_LOG = _DATA / "registry.log.jsonl"
_MEMBERS = _DATA / "members.jsonl"


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def build_service() -> RegistryService:
    repo = JsonlMemberRepository(_MEMBERS)
    base_logger = JsonlLogger(_LOG)
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


def build_handoff_state(events: list[dict]) -> dict:
    return {
        "from_organ": "registry",
        "handoff_to": "next_agent",
        "audit_log": str(_LOG.relative_to(_SANDBOX)),
        "rule": "keep audit JSONL raw; compress only the next-agent context",
        "event_digest": digest_events(events, keep=3),
    }


def print_handoff_state(events: list[dict]) -> None:
    state = build_handoff_state(events)
    compressor = TokenCompressor(prefer_yaml=False)
    compressed = compressor.compress(state)
    s = stats(state, compressed)
    print("[handoff] compressed state for next agent:")
    print(compressed)
    print(
        f"[handoff] context bytes {s['before_bytes']} -> {s['after_bytes']} "
        f"({s['saved_pct']}% saved); audit JSONL is unchanged"
    )


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "--demo"
    if mode == "--telegram":
        run(TelegramInbound())
    else:
        # เดโม: รวมเคสปกติ + ชื่อซ้ำ (ต้องถามก่อนสร้าง) + ชื่อผิดรูปแบบ
        before = len(read_jsonl(_LOG))
        run(DemoInbound(["alice", "alice", "x"]))
        print_handoff_state(read_jsonl(_LOG)[before:])
