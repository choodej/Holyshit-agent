from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_new_organ_includes_manifest_schema(tmp_path):
    repo_root = Path(__file__).resolve().parents[3]
    script = repo_root / ".claude" / "skills" / "organ-kit" / "scripts" / "new_organ.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "sample_manifest",
            "--title",
            "Sample Manifest",
            "--root",
            str(tmp_path),
        ],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
    schema = tmp_path / "sandbox" / "manifest.schema.json"
    check = tmp_path / "sandbox" / "tools" / "check.py"
    validate = tmp_path / "sandbox" / "tools" / "validate_manifests.py"
    manifest = tmp_path / "sandbox" / "organs" / "sample_manifest" / "manifest.json"
    checklist = tmp_path / "sandbox" / "organs" / "sample_manifest" / "CHECKLIST.md"
    deferred = tmp_path / "sandbox" / "organs" / "sample_manifest" / "DEFERRED.md"

    assert schema.exists()
    assert check.exists()
    assert validate.exists()
    data = json.loads(manifest.read_text(encoding="utf-8"))
    assert data["$schema"] == "../../manifest.schema.json"
    assert data["phase"] == "harness-proof"
    assert checklist.exists()
    assert deferred.exists()
