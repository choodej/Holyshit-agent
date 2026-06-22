from __future__ import annotations

import json

from organs.registry.app import build_handoff_state
from tools.token_compressor import TokenCompressor, stats


def test_handoff_state_digest_is_for_next_agent_context_only():
    events = [{"event": "register.created", "i": i} for i in range(12)] + [
        {"event": "register.rejected", "reason": "invalid_username"}
    ]

    state = build_handoff_state(events)

    assert state["audit_log"] == "organs/registry/.data/registry.log.jsonl"
    assert state["rule"] == "keep audit JSONL raw; compress only the next-agent context"
    assert state["event_digest"]["total"] == 13
    assert state["event_digest"]["counts"]["register.created"] == 12
    assert len(state["event_digest"]["recent"]) == 3


def test_handoff_state_compresses_for_agent_handoff():
    events = [{"event": "register.created", "i": i} for i in range(50)]
    state = build_handoff_state(events)

    text = TokenCompressor(prefer_yaml=False).compress(state)
    size = stats(state, text)

    assert json.loads(text)["event_digest"]["total"] == 50
    assert size["after_bytes"] < size["before_bytes"]
