"""พิสูจน์ว่าอวัยวะ 'registry' ทำงานจริง — domain + adapters JSONL ครบเส้น

ใช้ adapter จริง (JSONL บน tmp) ไม่ mock เพื่อพิสูจน์ว่าเชื่อมต่อกันติดจริง
"""
from __future__ import annotations

import json

from shared.result import Outcome

from organs.registry.adapters.jsonl_logger import JsonlLogger
from organs.registry.adapters.jsonl_member_repo import JsonlMemberRepository
from organs.registry.domain.registry_service import RegistryService


def _service(tmp_path):
    repo = JsonlMemberRepository(tmp_path / "members.jsonl")
    logger = JsonlLogger(tmp_path / "log.jsonl")
    return RegistryService(repo, logger), repo, logger


def test_register_success_and_persisted(tmp_path):
    service, repo, _ = _service(tmp_path)

    res = service.register("alice", source="demo")

    assert res.ok
    assert res.value.username == "alice"
    assert res.value.id.startswith("mbr_")
    # เก็บลงไฟล์จริง
    assert repo.exists_username("alice")
    assert repo.get(res.value.id).username == "alice"


def test_logging_happens(tmp_path):
    service, _, _ = _service(tmp_path)
    service.register("bob", source="demo")

    log_lines = (tmp_path / "log.jsonl").read_text(encoding="utf-8").splitlines()
    events = [json.loads(x)["event"] for x in log_lines]
    assert "register.created" in events


def test_duplicate_username_asks_before_creating(tmp_path):
    """กฎหลัก: ชื่อซ้ำต้อง 'ถามก่อนสร้าง' ไม่ใช่สร้างทับเงียบๆ"""
    service, repo, _ = _service(tmp_path)
    service.register("carol", source="demo")

    res = service.register("carol", source="demo")

    assert res.outcome is Outcome.NEEDS_DECISION
    assert res.choices, "ต้องมีทางเลือกให้คนตัดสินใจ"
    # ต้องมีทางเลือกที่ 'แนะนำ' หนึ่งอัน
    assert any(c.recommended for c in res.choices)
    # ต้องไม่มีสมาชิกซ้ำถูกสร้างเพิ่ม
    lines = (tmp_path / "members.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1


def test_invalid_username_rejected(tmp_path):
    service, _, _ = _service(tmp_path)
    res = service.register("x", source="demo")  # สั้นเกิน
    assert res.outcome is Outcome.REJECTED


def test_ids_are_unique_across_members(tmp_path):
    service, _, _ = _service(tmp_path)
    a = service.register("user_one", source="demo")
    b = service.register("user_two", source="demo")
    assert a.value.id != b.value.id
