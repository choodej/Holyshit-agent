"""token_compressor — shrink verbose JSON/logs into dense state for agent context.

Honest note: YAML is not reliably fewer tokens than JSON. The real, measurable
savings come from removing pretty-print whitespace, dropping empty values,
shortening repeated keys, and digesting repetitive records — NOT from the format
itself. This module does the things that actually save tokens, and can emit
compact JSON (default, no dependency) or YAML (only if PyYAML is installed).

IMPORTANT: use this for context/state snapshots passed to the next agent run.
Do NOT run it over the canonical JSONL audit log — that must stay intact.
"""
from __future__ import annotations

import json
from collections import Counter
from typing import Any

try:  # optional, not required
    import yaml  # type: ignore
    _HAS_YAML = True
except Exception:  # pragma: no cover - depends on environment
    _HAS_YAML = False


_EMPTY = (None, "", [], {}, ())


def strip_empty(obj: Any) -> Any:
    """Recursively drop None / empty string / empty containers (lossless-ish)."""
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            v2 = strip_empty(v)
            if v2 not in _EMPTY:
                out[k] = v2
        return out
    if isinstance(obj, list):
        return [strip_empty(v) for v in obj if strip_empty(v) not in _EMPTY]
    return obj


def digest_events(records: list[dict], keep: int = 20,
                  group_key: str = "event") -> dict:
    """Collapse a long event stream: counts per type + the last `keep` records.

    Lossy: use only for context snapshots, never for the audit log.
    """
    counts = Counter(r.get(group_key, "?") for r in records)
    return {
        "total": len(records),
        "counts": dict(counts),
        "recent": records[-keep:],
    }


class TokenCompressor:
    def __init__(self, prefer_yaml: bool = True) -> None:
        self._yaml = prefer_yaml and _HAS_YAML

    def render(self, obj: Any) -> str:
        """Densest available textual form."""
        if self._yaml:
            return yaml.safe_dump(obj, allow_unicode=True, default_flow_style=True,
                                  sort_keys=False, width=10_000).strip()
        return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

    def compress(self, data: Any, *, mode: str = "lossless", keep: int = 20) -> str:
        """mode='lossless' -> strip empties then render.
        mode='digest'   -> for a list of event dicts, summarize then render.
        """
        if mode == "digest" and isinstance(data, list):
            return self.render(digest_events(data, keep=keep))
        return self.render(strip_empty(data))


def stats(original: Any, compressed_text: str) -> dict:
    """Rough before/after byte sizes (a usable proxy for token volume)."""
    before = len(json.dumps(original, ensure_ascii=False, indent=2))
    after = len(compressed_text)
    saved = before - after
    return {
        "before_bytes": before,
        "after_bytes": after,
        "saved_bytes": saved,
        "saved_pct": round(100 * saved / before, 1) if before else 0.0,
    }


if __name__ == "__main__":
    import sys

    raw = sys.stdin.read()
    data = json.loads(raw) if raw.strip() else {}
    c = TokenCompressor()
    text = c.compress(data)
    sys.stderr.write(json.dumps(stats(data, text)) + "\n")
    print(text)
