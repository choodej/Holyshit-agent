"""RegistryService — หัวใจของอวัยวะ "สมัครสมาชิก"

กฎที่ฝังในตรรกะ:
  - validate username ก่อนเสมอ
  - ชื่อซ้ำ / id ซ้ำ -> ไม่สร้างทับเงียบๆ แต่คืน NEEDS_DECISION พร้อม "ทางเลือก"
    (สอดคล้องกฎ: ถามก่อนสร้าง + เสนอทางเลือก + แนะนำทางที่ดีที่สุด)
  - ทุกผลลัพธ์ถูก log ผ่าน Logger port

domain นี้ไม่ import telegram/db/clickup เลย — ทดสอบได้ด้วยตัวมันเอง
"""
from __future__ import annotations

import re
from datetime import datetime, timezone

from shared.ids import new_id, slugify
from shared.result import Choice, Result

from ..ports.logger import Logger
from ..ports.member_repo import MemberRepository
from .member import Member

_USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,32}$")


class RegistryService:
    def __init__(self, repo: MemberRepository, logger: Logger) -> None:
        self._repo = repo
        self._logger = logger

    def register(self, username: str, source: str = "unknown") -> Result[Member]:
        username = (username or "").strip()

        # 1) validate
        if not _USERNAME_RE.match(username):
            self._logger.emit("register.rejected", username=username, source=source,
                              reason="invalid_username")
            return Result.reject(
                "username ต้องเป็น a-z A-Z 0-9 _ ยาว 3-32 ตัว"
            )

        # 2) ชื่อซ้ำ -> ถามก่อน (ไม่สร้างทับ)
        if self._repo.exists_username(username):
            self._logger.emit("register.needs_decision", username=username, source=source,
                              reason="duplicate_username")
            return Result.decide(
                question=f"username '{username}' มีอยู่แล้ว จะทำอย่างไร?",
                reason="duplicate_username",
                choices=[
                    Choice("use_existing", "ใช้สมาชิกเดิม (ไม่สร้างใหม่)", recommended=True),
                    Choice("suggest_alt", f"สมัครชื่อใกล้เคียง เช่น '{username}_2'"),
                    Choice("force_new", "ยืนยันสร้างใหม่คนละ id (ชื่อซ้ำได้)"),
                    Choice("cancel", "ยกเลิก"),
                ],
            )

        # 3) สร้าง id ที่ไม่ชน (กันชนระดับ storage ด้วย)
        member_id = new_id("mbr")
        guard = 0
        while self._repo.exists_id(member_id):
            member_id = new_id("mbr")
            guard += 1
            if guard > 5:
                self._logger.emit("register.rejected", username=username, source=source,
                                  reason="id_collision_exhausted")
                return Result.reject("สร้าง id ไม่ซ้ำไม่สำเร็จ ลองใหม่อีกครั้ง")

        # 4) สร้างจริง + log
        member = Member(
            id=member_id,
            username=username,
            source=source,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._repo.save(member)
        self._logger.emit("register.created", id=member.id, username=member.username,
                          source=source)
        return Result.succeed(member)
