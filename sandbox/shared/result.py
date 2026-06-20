"""Result / Outcome — contract กลางสำหรับ "ปลอดภัยแต่ไม่ช้า"

แทนที่จะ throw exception มั่ว หรือสร้างของทับของเดิมเงียบๆ
ทุก use-case คืน Result ที่บอกชัดว่า:
  - OK            : ทำสำเร็จ
  - NEEDS_DECISION: เจอเคสเสี่ยง (id ซ้ำ/ชื่อซ้ำ/ทับของเดิม) -> คืน "ทางเลือก" ให้คนตัดสิน
  - REJECTED      : ข้อมูลไม่ผ่าน validate

อวัยวะไหนก็ใช้ตัวนี้ร่วมกันได้ ทำให้ behavior สม่ำเสมอทั้งระบบ
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class Outcome(str, Enum):
    OK = "ok"
    NEEDS_DECISION = "needs_decision"
    REJECTED = "rejected"


@dataclass(frozen=True)
class Choice:
    """หนึ่งทางเลือกที่จะเสนอให้คนตัดสินใจ (กฎ: เสนอทางเลือก + แนะนำทางที่ดีที่สุด)"""
    key: str
    label: str
    recommended: bool = False


@dataclass(frozen=True)
class Result(Generic[T]):
    outcome: Outcome
    value: T | None = None
    reason: str = ""
    question: str = ""
    choices: tuple[Choice, ...] = field(default_factory=tuple)

    @property
    def ok(self) -> bool:
        return self.outcome is Outcome.OK

    @property
    def needs_decision(self) -> bool:
        return self.outcome is Outcome.NEEDS_DECISION

    # --- factory helpers ---
    @staticmethod
    def succeed(value: T) -> "Result[T]":
        return Result(Outcome.OK, value=value)

    @staticmethod
    def reject(reason: str) -> "Result[Any]":
        return Result(Outcome.REJECTED, reason=reason)

    @staticmethod
    def decide(question: str, choices: list[Choice], reason: str = "") -> "Result[Any]":
        return Result(
            Outcome.NEEDS_DECISION,
            reason=reason,
            question=question,
            choices=tuple(choices),
        )
