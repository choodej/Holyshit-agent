"""Universal SafetyGate — human-in-the-loop guard for external writes.

Every adapter that performs an "external write" (DB insert, API POST, file send,
etc.) routes the action through a SafetyGate first. The gate can auto-approve
reversible work, or require explicit approval / show a dry-run preview for
risky work. This generalizes the project rule: "ask before doing risky things".

Reuses shared.result so adapters can surface a NEEDS_DECISION uniformly.
"""
from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, TypeVar

from .result import Choice, Result

T = TypeVar("T")


@dataclass(frozen=True)
class WriteIntent:
    """A described external write, shown to the gate before it happens."""
    action: str                 # e.g. "db.insert", "api.post", "telegram.send"
    target: str                 # e.g. "members table", "https://api.../tasks"
    payload: Any = None         # what would be written (for preview)
    reversible: bool = False     # can it be undone cheaply?

    def preview(self) -> str:
        try:
            body = json.dumps(self.payload, ensure_ascii=False, default=str)
        except TypeError:
            body = repr(self.payload)
        flag = "reversible" if self.reversible else "IRREVERSIBLE"
        return f"[DRY-RUN] {self.action} -> {self.target} ({flag})\n  payload: {body}"


@dataclass(frozen=True)
class Decision:
    approved: bool
    reason: str = ""


class SafetyGate(ABC):
    @abstractmethod
    def review(self, intent: WriteIntent) -> Decision: ...


class AutoApproveGate(SafetyGate):
    """Approves everything. Use only in trusted/automated contexts or tests."""

    def review(self, intent: WriteIntent) -> Decision:
        return Decision(True, "auto-approve")


class DryRunGate(SafetyGate):
    """Never writes. Prints a preview and denies — for rehearsals and tests."""

    def __init__(self, sink: Callable[[str], None] = print) -> None:
        self._sink = sink

    def review(self, intent: WriteIntent) -> Decision:
        self._sink(intent.preview())
        return Decision(False, "dry-run: not approved")


class PolicyGate(SafetyGate):
    """Tiered rule: reversible -> auto; irreversible -> needs explicit approval.

    approve_fn lets a human (or higher policy) approve irreversible writes.
    """

    def __init__(self, approve_fn: Callable[[WriteIntent], bool] | None = None,
                 auto_reversible: bool = True) -> None:
        self._approve_fn = approve_fn
        self._auto_reversible = auto_reversible

    def review(self, intent: WriteIntent) -> Decision:
        if self._auto_reversible and intent.reversible:
            return Decision(True, "auto: reversible")
        if self._approve_fn and self._approve_fn(intent):
            return Decision(True, "approved")
        return Decision(False, "irreversible write requires explicit approval")


class ExternalWriteAdapter:
    """Base for adapters that write to the outside world.

    Subclasses call self.guarded(intent, do_write) instead of writing directly.
    Enforcement is by convention + this base class (Python can't force it).
    """

    def __init__(self, gate: SafetyGate) -> None:
        self._gate = gate

    def guarded(self, intent: WriteIntent, do_write: Callable[[], T]) -> Result[T]:
        decision = self._gate.review(intent)
        if not decision.approved:
            return Result.decide(
                question=f"External write '{intent.action}' -> {intent.target} needs approval",
                reason=decision.reason,
                choices=[
                    Choice("cancel", "Cancel (do not write)", recommended=True),
                    Choice("approve", "Approve and write"),
                ],
            )
        return Result.succeed(do_write())
