"""graphify — generate the system map from every organ's manifest.json, and
detect "shadows" (overlaps / circular deps / dangling deps).

Rule: the catalog/graph is generated from organ manifest contracts, never
hand-written. Keep each manifest synced with code; `tools/validate_manifests.py`
guards the parts this framework can check cheaply. Outputs:
  - CATALOG.md   (human index)
  - graph.json   (machine graph)
  - graph.mmd    (Mermaid.js diagram)

Validation (shadow detection) exits non-zero when issues are found, so it can
gate CI. Detection functions take plain manifest dicts and are unit-testable.

Run: python tools/graphify.py        (add --strict to fail on warnings too)
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

SANDBOX = Path(__file__).resolve().parents[1]
ORGANS = SANDBOX / "organs"


# --------------------------------------------------------------------------- #
# load
# --------------------------------------------------------------------------- #
def load_manifests(organs_dir: Path = ORGANS) -> list[dict]:
    out = []
    for mf in sorted(organs_dir.glob("*/manifest.json")):
        data = json.loads(mf.read_text(encoding="utf-8"))
        data["_path"] = str(mf.parent.relative_to(organs_dir.parent))
        out.append(data)
    return out


# --------------------------------------------------------------------------- #
# shadow detection (pure functions — unit-testable)
# --------------------------------------------------------------------------- #
def detect_cycles(manifests: list[dict]) -> list[str]:
    graph = {m["organ"]: list(m.get("depends_on", [])) for m in manifests}
    warnings: list[str] = []
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in graph}

    def dfs(node: str, stack: list[str]) -> None:
        color[node] = GRAY
        for dep in graph.get(node, []):
            if dep not in color:
                continue  # dangling handled separately
            if color[dep] == GRAY:
                cycle = " -> ".join(stack[stack.index(dep):] + [dep])
                warnings.append(f"circular dependency: {cycle}")
            elif color[dep] == WHITE:
                dfs(dep, stack + [dep])
        color[node] = BLACK

    for n in graph:
        if color[n] == WHITE:
            dfs(n, [n])
    return warnings


def detect_dangling(manifests: list[dict]) -> list[str]:
    names = {m["organ"] for m in manifests}
    out = []
    for m in manifests:
        for dep in m.get("depends_on", []):
            if dep not in names:
                out.append(f"organ '{m['organ']}' depends on missing organ '{dep}'")
    return out


def detect_data_overlap(manifests: list[dict]) -> list[str]:
    """Two organs claiming the same data domain (owns_data) = a shadow."""
    owners: dict[str, list[str]] = {}
    for m in manifests:
        for data in m.get("owns_data", []):
            owners.setdefault(data.lower(), []).append(m["organ"])
    out = []
    for data, who in owners.items():
        if len(who) > 1:
            out.append(f"data overlap: '{data}' is owned by {', '.join(sorted(who))}")
    return out


def detect_unguarded_writes(manifests: list[dict]) -> list[str]:
    """Organ declares external_writes but no safety_gate -> risky shadow."""
    out = []
    for m in manifests:
        if m.get("external_writes") and not m.get("safety_gate"):
            out.append(f"organ '{m['organ']}' does external writes without a safety_gate")
    return out


def detect_shadows(manifests: list[dict]) -> list[str]:
    return (
        detect_cycles(manifests)
        + detect_dangling(manifests)
        + detect_data_overlap(manifests)
        + detect_unguarded_writes(manifests)
    )


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def manifest_phase(manifest: dict) -> str:
    return manifest.get("phase") or manifest.get("status", "?")


def build_graph(manifests: list[dict]) -> dict:
    nodes = [{"id": m["organ"], "title": m.get("title", ""),
              "phase": manifest_phase(m), "status": m.get("status", ""),
              "path": m.get("_path", "")}
             for m in manifests]
    edges = [{"from": m["organ"], "to": dep}
             for m in manifests for dep in m.get("depends_on", [])]
    return {"nodes": nodes, "edges": edges}


def render_mermaid(manifests: list[dict]) -> str:
    lines = ["graph TD"]
    for m in manifests:
        organ = m["organ"]
        lines.append(f'  {organ}["{organ}\\n({manifest_phase(m)})"]')
        for port, adapters in (m.get("adapters") or {}).items():
            for ad in adapters:
                node = f"{organ}__{ad}"
                lines.append(f'  {node}(["{ad}"])')
                lines.append(f"  {organ} -. {port} .-> {node}")
    for m in manifests:
        for dep in m.get("depends_on", []):
            lines.append(f"  {m['organ']} ==> {dep}")
    return "\n".join(lines) + "\n"


def render_catalog(manifests: list[dict], warnings: list[str]) -> str:
    lines = ["# CATALOG — system index (auto-generated, do not edit by hand)", ""]
    lines.append(f"Organs: {len(manifests)}")
    phase_counts = Counter(manifest_phase(m) for m in manifests)
    if phase_counts:
        lines.append("")
        lines.append("## Phases")
        for phase, count in sorted(phase_counts.items()):
            lines.append(f"- `{phase}`: {count}")
    if warnings:
        lines.append("")
        lines.append("## ⚠ Shadow warnings")
        for w in warnings:
            lines.append(f"- {w}")
    lines.append("")
    for m in manifests:
        lines.append(f"## {m['organ']} — {m.get('title', '')}")
        lines.append(
            f"- phase: `{manifest_phase(m)}` | status: `{m.get('status', '?')}` "
            f"| version: `{m.get('version', '?')}`"
        )
        lines.append(f"- path: `{m.get('_path', '')}`")
        lines.append(f"- purpose: {m.get('purpose', '')}")
        lines.append(f"- ports: {', '.join(m.get('ports', [])) or '-'}")
        deps = m.get("depends_on", [])
        lines.append(f"- depends on: {', '.join(deps) if deps else '(independent)'}")
        lines.append("")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Build system map + detect shadows.")
    ap.add_argument("--strict", action="store_true",
                    help="exit non-zero if any shadow warning is found")
    args = ap.parse_args(argv)

    manifests = load_manifests()
    warnings = detect_shadows(manifests)
    graph = build_graph(manifests)

    (SANDBOX / "graph.json").write_text(
        json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
    (SANDBOX / "graph.mmd").write_text(render_mermaid(manifests), encoding="utf-8")
    (SANDBOX / "CATALOG.md").write_text(
        render_catalog(manifests, warnings), encoding="utf-8")

    print(f"OK: mapped {len(manifests)} organ(s) -> CATALOG.md, graph.json, graph.mmd")
    for w in warnings:
        print(f"  warning: {w}")
    if warnings and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
