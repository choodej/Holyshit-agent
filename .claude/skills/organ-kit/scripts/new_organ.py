#!/usr/bin/env python3
"""new_organ.py — scaffold a new, self-contained organ from the organ-kit template.

Runs without any AI. Project-agnostic.

Usage:
    python new_organ.py <organ_name> [--title "Human title"]
                        [--dir sandbox/organs] [--root .]

Guarantees (the kit's rules):
  - refuses if the organ already exists (ask-before-create; never overwrites)
  - ensures shared/ and tools/ exist once (created, never overwritten)
  - the new organ already runs and passes its smoke test
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = SKILL_ROOT / "templates"

_NAME_RE = re.compile(r"^[a-z][a-z0-9_]{2,30}$")


def _render(text: str, ctx: dict[str, str]) -> str:
    for key, val in ctx.items():
        text = text.replace("{{" + key + "}}", val)
    return text


def _copy_tree(src: Path, dst: Path, ctx: dict[str, str], *, overwrite: bool) -> int:
    """Render every file under src into dst. Returns number of files written."""
    written = 0
    for path in sorted(src.rglob("*")):
        if path.is_dir():
            continue
        rel = path.relative_to(src)
        target = dst / rel
        if target.exists() and not overwrite:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        content = path.read_text(encoding="utf-8")
        target.write_text(_render(content, ctx), encoding="utf-8")
        written += 1
    return written


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Scaffold a new organ.")
    ap.add_argument("organ", help="organ name: lowercase, a-z 0-9 _, 3-31 chars")
    ap.add_argument("--title", default=None, help="human-readable title")
    ap.add_argument("--dir", default="sandbox/organs",
                    help="organs directory relative to --root (default: sandbox/organs)")
    ap.add_argument("--root", default=".", help="project root (default: current dir)")
    args = ap.parse_args(argv)

    organ = args.organ.strip().lower()
    if not _NAME_RE.match(organ):
        print(f"error: invalid organ name '{organ}' "
              f"(use lowercase a-z 0-9 _, 3-31 chars, start with a letter)",
              file=sys.stderr)
        return 2

    class_name = "".join(p.capitalize() for p in organ.split("_"))
    title = args.title or organ
    id_prefix = re.sub(r"[^a-z0-9]", "", organ)[:3] or "itm"

    ctx = {"ORGAN": organ, "CLASS": class_name, "TITLE": title, "ID_PREFIX": id_prefix}

    root = Path(args.root).resolve()
    organs_dir = root / args.dir
    organ_dir = organs_dir / organ
    sandbox_root = organs_dir.parent              # e.g. .../sandbox
    shared_dir = sandbox_root / "shared"
    tools_dir = sandbox_root / "tools"

    # ask-before-create: never overwrite an existing organ
    if organ_dir.exists():
        print(f"error: organ '{organ}' already exists at {organ_dir}\n"
              f"       choose another name or remove it deliberately first.",
              file=sys.stderr)
        return 3

    # ensure shared/ and tools/ (created once, never overwritten)
    n_shared = _copy_tree(TEMPLATES / "shared", shared_dir, ctx, overwrite=False)
    n_tools = _copy_tree(TEMPLATES / "tools", tools_dir, ctx, overwrite=False)
    # ensure organs/ is a package
    (organs_dir / "__init__.py").parent.mkdir(parents=True, exist_ok=True)
    (organs_dir / "__init__.py").touch(exist_ok=True)

    # stamp the organ
    n_organ = _copy_tree(TEMPLATES / "organ", organ_dir, ctx, overwrite=True)

    rel_organ = organ_dir.relative_to(root)
    print(f"OK: created organ '{organ}' ({n_organ} files) at {rel_organ}")
    if n_shared:
        print(f"    + initialized shared/ ({n_shared} files)")
    if n_tools:
        print(f"    + initialized tools/ ({n_tools} files)")
    print("\nNext:")
    print(f"  cd {sandbox_root.relative_to(root)}")
    print(f"  python -m pytest organs/{organ}/tests -q")
    print(f"  python organs/{organ}/app.py --demo")
    print(f"  python tools/build_graph.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
