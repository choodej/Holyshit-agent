from __future__ import annotations

from pathlib import Path

from tools.validate_manifests import validate_all, validate_manifest_data


def _schema() -> dict:
    return {
        "required": [
            "organ",
            "title",
            "version",
            "language",
            "phase",
            "status",
            "purpose",
            "ports",
            "adapters",
            "exposes",
            "depends_on",
            "owns_data",
        ],
        "properties": {
            "organ": {"type": "string", "pattern": "^[a-z][a-z0-9_]{2,30}$"},
            "title": {"type": "string"},
            "version": {"type": "string"},
            "language": {"type": "string"},
            "phase": {"type": "string", "enum": ["skeleton", "slice-proven"]},
            "status": {"type": "string"},
            "purpose": {"type": "string"},
            "ports": {"type": "array"},
            "adapters": {"type": "object"},
            "exposes": {"type": "array"},
            "depends_on": {
                "type": "array",
                "items": {"pattern": "^[a-z][a-z0-9_]{2,30}$"},
            },
            "owns_data": {"type": "array"},
            "external_writes": {"type": "array"},
            "safety_gate": {"type": "boolean"},
        },
    }


def _valid_manifest() -> dict:
    return {
        "organ": "sample",
        "title": "Sample",
        "version": "0.1.0",
        "language": "python",
        "phase": "slice-proven",
        "status": "slice-proven",
        "purpose": "Prove a sample slice.",
        "ports": ["Repository"],
        "adapters": {"Repository": ["jsonl_repository"]},
        "exposes": ["submit(label, source) -> Result[Item]"],
        "depends_on": [],
        "owns_data": ["sample.jsonl"],
    }


def _organ_dir(tmp_path: Path, phase: str = "slice-proven") -> Path:
    organ_dir = tmp_path / "sample"
    organ_dir.mkdir()
    (organ_dir / "CHECKLIST.md").write_text(
        f"# Checklist\n\nCurrent phase: `{phase}`\n", encoding="utf-8"
    )
    return organ_dir


def test_accepts_valid_manifest_with_matching_checklist(tmp_path):
    errors = validate_manifest_data(
        _valid_manifest(), organ_dir=_organ_dir(tmp_path), schema=_schema()
    )
    assert errors == []


def test_requires_safety_gate_for_external_writes(tmp_path):
    manifest = _valid_manifest()
    manifest["external_writes"] = ["clickup.create_task"]

    errors = validate_manifest_data(
        manifest, organ_dir=_organ_dir(tmp_path), schema=_schema()
    )

    assert any("safety_gate: true" in error for error in errors)


def test_rejects_external_write_adapter_not_declared_in_manifest(tmp_path):
    manifest = _valid_manifest()
    organ_dir = _organ_dir(tmp_path)
    adapters = organ_dir / "adapters"
    adapters.mkdir()
    (adapters / "clickup_logger.py").write_text(
        "from shared.safety import ExternalWriteAdapter\n"
        "class ClickUpLogger(ExternalWriteAdapter):\n"
        "    pass\n",
        encoding="utf-8",
    )

    errors = validate_manifest_data(manifest, organ_dir=organ_dir, schema=_schema())

    assert any("external_writes" in error and "ExternalWriteAdapter" in error for error in errors)
    assert any("safety_gate: true" in error and "ExternalWriteAdapter" in error for error in errors)


def test_accepts_declared_external_write_adapter(tmp_path):
    manifest = _valid_manifest()
    manifest["external_writes"] = ["clickup.create_task"]
    manifest["safety_gate"] = True
    organ_dir = _organ_dir(tmp_path)
    adapters = organ_dir / "adapters"
    adapters.mkdir()
    (adapters / "clickup_logger.py").write_text(
        "from shared.safety import ExternalWriteAdapter\n"
        "class ClickUpLogger(ExternalWriteAdapter):\n"
        "    pass\n",
        encoding="utf-8",
    )

    errors = validate_manifest_data(manifest, organ_dir=organ_dir, schema=_schema())

    assert errors == []


def test_rejects_checklist_phase_drift(tmp_path):
    errors = validate_manifest_data(
        _valid_manifest(), organ_dir=_organ_dir(tmp_path, phase="skeleton"), schema=_schema()
    )

    assert any("must match manifest phase" in error for error in errors)


def test_live_manifests_are_valid():
    assert validate_all() == []
