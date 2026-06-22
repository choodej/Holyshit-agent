from __future__ import annotations

import json
import re
from pathlib import Path


def _read_phase(checklist: Path) -> str:
    text = checklist.read_text(encoding="utf-8")
    match = re.search(r"^Current phase: `([^`]+)`$", text, re.MULTILINE)
    assert match, f"missing Current phase line in {checklist}"
    return match.group(1)


def test_live_checklist_phase_matches_manifest():
    sandbox = Path(__file__).resolve().parents[2]
    for manifest in sorted((sandbox / "organs").glob("*/manifest.json")):
        checklist = manifest.with_name("CHECKLIST.md")
        data = json.loads(manifest.read_text(encoding="utf-8"))
        assert checklist.exists(), f"missing checklist for {manifest}"
        assert _read_phase(checklist) == data["phase"]


def test_template_checklist_phase_matches_manifest_template():
    repo_root = Path(__file__).resolve().parents[3]
    template_dir = repo_root / ".claude" / "skills" / "organ-kit" / "templates" / "organ"
    manifest = json.loads((template_dir / "manifest.json").read_text(encoding="utf-8"))
    assert _read_phase(template_dir / "CHECKLIST.md") == manifest["phase"]


def _assert_external_write_requires_safety_gate(schema_path: Path) -> None:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    rules = schema["allOf"]
    assert any(
        rule.get("if", {})
        .get("properties", {})
        .get("external_writes", {})
        .get("minItems") == 1
        and rule.get("then", {})
        .get("properties", {})
        .get("safety_gate", {})
        .get("const") is True
        for rule in rules
    )


def test_manifest_schema_requires_safety_gate_for_external_writes():
    repo_root = Path(__file__).resolve().parents[3]
    _assert_external_write_requires_safety_gate(
        repo_root / "sandbox" / "manifest.schema.json"
    )
    _assert_external_write_requires_safety_gate(
        repo_root / ".claude" / "skills" / "organ-kit" / "templates" / "manifest.schema.json"
    )
