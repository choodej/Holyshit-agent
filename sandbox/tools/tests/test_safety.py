"""Tests for the universal SafetyGate."""
from __future__ import annotations

from shared.result import Outcome
from shared.safety import (
    AutoApproveGate,
    DryRunGate,
    ExternalWriteAdapter,
    PolicyGate,
    WriteIntent,
)


def _intent(reversible: bool) -> WriteIntent:
    return WriteIntent(action="api.post", target="https://x/y",
                       payload={"a": 1}, reversible=reversible)


def test_policy_auto_approves_reversible():
    gate = PolicyGate()
    assert gate.review(_intent(reversible=True)).approved is True


def test_policy_blocks_irreversible_without_callback():
    gate = PolicyGate()
    assert gate.review(_intent(reversible=False)).approved is False


def test_policy_allows_irreversible_with_callback():
    gate = PolicyGate(approve_fn=lambda intent: True)
    assert gate.review(_intent(reversible=False)).approved is True


def test_dry_run_never_approves_and_previews():
    seen = []
    gate = DryRunGate(sink=seen.append)
    decision = gate.review(_intent(reversible=True))
    assert decision.approved is False
    assert seen and "DRY-RUN" in seen[0]


def test_guarded_adapter_blocks_and_returns_decision():
    """An external write that is not approved must NOT execute."""
    wrote = []

    class FakeWriter(ExternalWriteAdapter):
        def post(self):
            return self.guarded(_intent(reversible=False),
                                lambda: wrote.append("did write") or "ok")

    res = FakeWriter(PolicyGate()).post()  # irreversible + no approver -> blocked
    assert res.outcome is Outcome.NEEDS_DECISION
    assert wrote == []  # write did not happen
    assert any(c.recommended for c in res.choices)


def test_guarded_adapter_writes_when_approved():
    wrote = []

    class FakeWriter(ExternalWriteAdapter):
        def post(self):
            return self.guarded(_intent(reversible=True),
                                lambda: wrote.append("did write") or "ok")

    res = FakeWriter(AutoApproveGate()).post()
    assert res.ok
    assert wrote == ["did write"]
