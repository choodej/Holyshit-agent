"""Result / Outcome — shared contract for "safe but not slow".

Instead of throwing or silently overwriting, every use-case returns a Result:
  - OK             : done
  - NEEDS_DECISION : risky case (duplicate id/name, overwrite) -> return choices
  - REJECTED       : input failed validation
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

    @staticmethod
    def succeed(value: T) -> "Result[T]":
        return Result(Outcome.OK, value=value)

    @staticmethod
    def reject(reason: str) -> "Result[Any]":
        return Result(Outcome.REJECTED, reason=reason)

    @staticmethod
    def decide(question: str, choices: list[Choice], reason: str = "") -> "Result[Any]":
        return Result(Outcome.NEEDS_DECISION, reason=reason, question=question,
                      choices=tuple(choices))
