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
    manifest = tmp_path / "sandbox" / "organs" / "sample_manifest" / "manifest.json"

    assert schema.exists()
    assert json.loads(manifest.read_text(encoding="utf-8"))["$schema"] == "../../manifest.schema.json"
