#!/usr/bin/env python3
"""Validate organ manifest files and their skeleton-first checklist phase.

This is intentionally small and stdlib-only. The schema remains the documented
contract; this command enforces the parts graphify and beginners depend on.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

SANDBOX = Path(__file__).resolve().parents[1]
ORGANS = SANDBOX / "organs"
SCHEMA = SANDBOX / "manifest.schema.json"

_CHECKLIST_PHASE_RE = re.compile(r"^Current phase: `([^`]+)`$", re.MULTILINE)
_EXTERNAL_WRITE_MARKERS = ("ExternalWriteAdapter", "WriteIntent(", ".guarded(")


def _schema() -> dict[str, Any]:
    return json.loads(SCHEMA.read_text(encoding="utf-8"))


def _type_name(value: Any) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def _expect_type(path: str, value: Any, expected: str) -> list[str]:
    if _type_name(value) != expected:
        return [f"{path}: expected {expected}, got {_type_name(value)}"]
    return []


def _validate_string_array(path: str, values: Any, *, pattern: str | None = None) -> list[str]:
    errors = _expect_type(path, values, "array")
    if errors:
        return errors
    seen: set[str] = set()
    out: list[str] = []
    matcher = re.compile(pattern) if pattern else None
    for idx, item in enumerate(values):
        item_path = f"{path}[{idx}]"
        out += _expect_type(item_path, item, "string")
        if not isinstance(item, str):
            continue
        if not item:
            out.append(f"{item_path}: must not be empty")
        if matcher and not matcher.match(item):
            out.append(f"{item_path}: does not match {pattern}")
        if item in seen:
            out.append(f"{path}: duplicate item {item!r}")
        seen.add(item)
    return out


def checklist_phase(checklist: Path) -> str | None:
    if not checklist.exists():
        return None
    match = _CHECKLIST_PHASE_RE.search(checklist.read_text(encoding="utf-8"))
    return match.group(1) if match else None


def external_write_markers(organ_dir: Path) -> list[str]:
    """Return adapter files that look like SafetyGate-backed external writes.

    This is deliberately narrow. It checks this repo's convention, not every
    possible Python network/file write.
    """
    adapters_dir = organ_dir / "adapters"
    if not adapters_dir.exists():
        return []
    marked: list[str] = []
    for path in sorted(adapters_dir.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        if any(marker in text for marker in _EXTERNAL_WRITE_MARKERS):
            marked.append(str(path.relative_to(organ_dir)))
    return marked


def validate_manifest_data(data: dict[str, Any], *, organ_dir: Path, schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    props = schema["properties"]

    for field in schema["required"]:
        if field not in data:
            errors.append(f"{organ_dir.name}/manifest.json: missing required field {field!r}")

    for field, spec in props.items():
        if field not in data:
            continue
        expected = spec.get("type")
        if expected:
            errors += _expect_type(f"{organ_dir.name}/manifest.json:{field}", data[field], expected)

    if isinstance(data.get("organ"), str):
        pattern = props["organ"]["pattern"]
        if not re.match(pattern, data["organ"]):
            errors.append(f"{organ_dir.name}/manifest.json:organ does not match {pattern}")
        if data["organ"] != organ_dir.name:
            errors.append(
                f"{organ_dir.name}/manifest.json: organ {data['organ']!r} must match folder {organ_dir.name!r}"
            )

    if isinstance(data.get("phase"), str):
        phases = props["phase"]["enum"]
        if data["phase"] not in phases:
            errors.append(f"{organ_dir.name}/manifest.json:phase must be one of {', '.join(phases)}")

    if "ports" in data:
        errors += _validate_string_array(f"{organ_dir.name}/manifest.json:ports", data["ports"])
    if "exposes" in data:
        errors += _validate_string_array(f"{organ_dir.name}/manifest.json:exposes", data["exposes"])
    if "owns_data" in data:
        errors += _validate_string_array(f"{organ_dir.name}/manifest.json:owns_data", data["owns_data"])
    if "depends_on" in data:
        errors += _validate_string_array(
            f"{organ_dir.name}/manifest.json:depends_on",
            data["depends_on"],
            pattern=props["depends_on"]["items"]["pattern"],
        )
    if "external_writes" in data:
        errors += _validate_string_array(
            f"{organ_dir.name}/manifest.json:external_writes", data["external_writes"]
        )
        if isinstance(data["external_writes"], list) and data["external_writes"]:
            if data.get("safety_gate") is not True:
                errors.append(
                    f"{organ_dir.name}/manifest.json: external_writes requires safety_gate: true"
                )

    write_markers = external_write_markers(organ_dir)
    if write_markers:
        marker_list = ", ".join(write_markers)
        if not data.get("external_writes"):
            errors.append(
                f"{organ_dir.name}/manifest.json: adapter code uses ExternalWriteAdapter/WriteIntent "
                f"but external_writes is empty or missing ({marker_list})"
            )
        if data.get("safety_gate") is not True:
            errors.append(
                f"{organ_dir.name}/manifest.json: adapter code uses ExternalWriteAdapter/WriteIntent "
                f"but safety_gate: true is missing ({marker_list})"
            )

    adapters = data.get("adapters")
    if isinstance(adapters, dict):
        for port, adapter_ids in adapters.items():
            if not isinstance(port, str) or not port:
                errors.append(f"{organ_dir.name}/manifest.json:adapters has an empty/non-string port")
                continue
            errors += _validate_string_array(
                f"{organ_dir.name}/manifest.json:adapters.{port}", adapter_ids
            )

    phase = data.get("phase")
    checklist = organ_dir / "CHECKLIST.md"
    recorded_phase = checklist_phase(checklist)
    if recorded_phase is None:
        errors.append(f"{organ_dir.name}/CHECKLIST.md: missing Current phase line")
    elif phase != recorded_phase:
        errors.append(
            f"{organ_dir.name}/CHECKLIST.md: phase {recorded_phase!r} must match manifest phase {phase!r}"
        )

    return errors


def validate_manifest_file(manifest: Path, *, schema: dict[str, Any]) -> list[str]:
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{manifest}: invalid JSON: {exc}"]
    if not isinstance(data, dict):
        return [f"{manifest}: expected a JSON object"]
    return validate_manifest_data(data, organ_dir=manifest.parent, schema=schema)


def validate_all(organs_dir: Path = ORGANS) -> list[str]:
    schema = _schema()
    errors: list[str] = []
    for manifest in sorted(organs_dir.glob("*/manifest.json")):
        errors += validate_manifest_file(manifest, schema=schema)
    if not errors and not list(organs_dir.glob("*/manifest.json")):
        errors.append(f"{organs_dir}: no organ manifests found")
    return errors


def main(argv: list[str] | None = None) -> int:
    del argv
    errors = validate_all()
    if errors:
        print("manifest validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print("OK: organ manifests are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
