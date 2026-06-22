"""Reference adapter: an EXTERNAL WRITE done the safe way (rule 7 / RULES.md §7).

This is an optional template you copy when an organ must write to the outside
world (DB insert, API POST, message send). It is NOT wired into app.py by
default — delete it if '{{ORGAN}}' has no external writes.

The point: never POST/INSERT directly. Describe the write as a WriteIntent and
route it through a SafetyGate via ExternalWriteAdapter.guarded(). Default gate is
DryRunGate (preview + never write), so nothing escapes silently. Swap in
AutoApproveGate / PolicyGate when you're ready to write for real.

When you use this, also declare it in manifest.json so graphify can verify it:
    "external_writes": ["{{ORGAN}}.create"],
    "safety_gate": true
(Omitting safety_gate makes `python tools/graphify.py --strict` flag a shadow.)
"""
from __future__ import annotations

from shared.result import Result
from shared.safety import DryRunGate, ExternalWriteAdapter, SafetyGate, WriteIntent


class {{CLASS}}ExternalWriter(ExternalWriteAdapter):
    def __init__(self, endpoint: str, gate: SafetyGate | None = None) -> None:
        super().__init__(gate or DryRunGate())   # safe by default
        self._endpoint = endpoint

    def create(self, payload: dict) -> Result[str]:
        intent = WriteIntent(
            action="{{ORGAN}}.create",
            target=self._endpoint,
            payload=payload,
            reversible=False,          # set True only if it can be cheaply undone
        )
        # guarded() returns NEEDS_DECISION (no write) if the gate denies.
        return self.guarded(intent, lambda: self._do_write(payload))

    def _do_write(self, payload: dict) -> str:
        # TODO: real I/O here, e.g. requests.post(self._endpoint, json=payload)
        return "written"
