"""Tests for the token compressor."""
from __future__ import annotations

import json

from tools.token_compressor import (
    TokenCompressor,
    digest_events,
    stats,
    strip_empty,
)


def test_strip_empty_drops_null_and_empties():
    data = {"a": 1, "b": None, "c": "", "d": [], "e": {"x": None}, "f": {"y": 2}}
    out = strip_empty(data)
    assert out == {"a": 1, "f": {"y": 2}}


def test_lossless_is_smaller_than_pretty_json():
    data = {"name": "alice", "tags": ["x", "y"], "empty": None, "note": ""}
    text = TokenCompressor(prefer_yaml=False).compress(data)
    s = stats(data, text)
    assert s["after_bytes"] < s["before_bytes"]
    assert s["saved_pct"] > 0
    # round-trip of the kept content (compact JSON path)
    assert json.loads(text) == {"name": "alice", "tags": ["x", "y"]}


def test_digest_collapses_event_stream():
    records = [{"event": "created"} for _ in range(50)] + \
              [{"event": "rejected"} for _ in range(5)]
    d = digest_events(records, keep=10)
    assert d["total"] == 55
    assert d["counts"]["created"] == 50
    assert d["counts"]["rejected"] == 5
    assert len(d["recent"]) == 10


def test_compress_digest_mode_shrinks_large_log():
    records = [{"event": "tick", "i": i} for i in range(200)]
    text = TokenCompressor(prefer_yaml=False).compress(records, mode="digest", keep=5)
    s = stats(records, text)
    assert s["after_bytes"] < s["before_bytes"]
