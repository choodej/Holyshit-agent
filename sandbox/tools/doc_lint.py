#!/usr/bin/env python3
"""Small doc lint for rule-like docs.

The goal is not prose style. It catches the drift patterns this repo cares
about: rule docs that do not declare authority, do not route to RULES.md, or do
not point agents at the one check gate.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_RULES = ".claude/skills/organ-kit/reference/RULES.md"
CHECK_GATE = "python tools/check.py"
DECISION_GATE = "§10"

ROUTING_DOCS = [
    "AGENTS.md",
    "CLAUDE.md",
    "README.md",
    ".claude/skills/organ-kit/SKILL.md",
    "PROMPTS.md",
    "ANTI_DRIFT_EXAMPLES.md",
]

DOC_CONTRACT_FIELDS = [
    "**Scope:**",
    "**Authority:**",
    "**Enforcement:**",
    "**Example:**",
    "**Failure mode:**",
]


def _read(root: Path, rel_path: str) -> str | None:
    path = root / rel_path
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def lint_docs(root: Path = REPO_ROOT) -> list[str]:
    errors: list[str] = []
    texts: dict[str, str] = {}

    for rel_path in ROUTING_DOCS:
        text = _read(root, rel_path)
        if text is None:
            errors.append(f"{rel_path}: missing rule-like doc")
            continue
        texts[rel_path] = text

    agents = texts.get("AGENTS.md", "")
    for field in DOC_CONTRACT_FIELDS:
        if field not in agents:
            errors.append(f"AGENTS.md: missing doc contract field {field}")
    if "Do not create a second source of truth" not in agents:
        errors.append("AGENTS.md: missing second-source-of-truth guard")

    examples = texts.get("ANTI_DRIFT_EXAMPLES.md", "")
    for token in ("## หลงทาง", "## ถูกทาง"):
        if token not in examples:
            errors.append(f"ANTI_DRIFT_EXAMPLES.md: missing example section {token}")

    rules = _read(root, CANONICAL_RULES)
    if rules is None:
        errors.append(f"{CANONICAL_RULES}: missing canonical rules")
    elif "## 10. Human Decision Gate" not in rules:
        errors.append(f"{CANONICAL_RULES}: missing Human Decision Gate rule")

    for rel_path, text in texts.items():
        if rel_path != "AGENTS.md" and "RULES.md" not in text and CANONICAL_RULES not in text:
            errors.append(f"{rel_path}: must route to RULES.md instead of becoming canonical")
        if CHECK_GATE not in text:
            errors.append(f"{rel_path}: must mention the one check gate `{CHECK_GATE}`")
        if DECISION_GATE not in text:
            errors.append(f"{rel_path}: must route major decisions to RULES.md §10")

    return errors


def main(argv: list[str] | None = None) -> int:
    del argv
    errors = lint_docs()
    if errors:
        print("doc lint failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print("OK: rule-like docs route to the canonical spine")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
