#!/usr/bin/env python3
"""One gate before reporting success or promoting work."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SANDBOX = Path(__file__).resolve().parents[1]


def check_steps() -> list[tuple[str, list[str]]]:
    return [
        ("tests", [sys.executable, "-m", "pytest", "-q"]),
        ("doc lint", [sys.executable, "tools/doc_lint.py"]),
        ("manifest validation", [sys.executable, "tools/validate_manifests.py"]),
        ("strict graph", [sys.executable, "tools/graphify.py", "--strict"]),
        ("generated graph drift", ["git", "diff", "--exit-code", "CATALOG.md", "graph.json", "graph.mmd"]),
    ]


def main(argv: list[str] | None = None) -> int:
    del argv
    for label, command in check_steps():
        print(f"\n== {label} ==", flush=True)
        result = subprocess.run(command, cwd=SANDBOX)
        if result.returncode != 0:
            print(f"\nFAILED: {label}", file=sys.stderr)
            return result.returncode
    print("\nOK: check gate passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
