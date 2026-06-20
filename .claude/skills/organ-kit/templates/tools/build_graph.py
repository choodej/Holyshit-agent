"""graphify — generate the system catalog from each organ's manifest.json.

Rule: the catalog/graph is generated from code only, never hand-written, so it
cannot drift. Outputs CATALOG.md (for humans) and graph.json (for machines).

Run: python tools/build_graph.py
"""
from __future__ import annotations

import json
from pathlib import Path

SANDBOX = Path(__file__).resolve().parents[1]
ORGANS = SANDBOX / "organs"


def load_manifests() -> list[dict]:
    out = []
    for mf in sorted(ORGANS.glob("*/manifest.json")):
        data = json.loads(mf.read_text(encoding="utf-8"))
        data["_path"] = str(mf.parent.relative_to(SANDBOX))
        out.append(data)
    return out


def build_graph(manifests: list[dict]) -> dict:
    nodes = [{"id": m["organ"], "title": m.get("title", ""),
              "status": m.get("status", ""), "path": m["_path"]} for m in manifests]
    edges = []
    for m in manifests:
        for dep in m.get("depends_on", []):
            edges.append({"from": m["organ"], "to": dep})
    return {"nodes": nodes, "edges": edges}


def render_catalog(manifests: list[dict]) -> str:
    lines = ["# CATALOG — system index (auto-generated, do not edit by hand)", ""]
    lines.append(f"Organs: {len(manifests)}")
    lines.append("")
    for m in manifests:
        lines.append(f"## {m['organ']} — {m.get('title', '')}")
        lines.append(f"- status: `{m.get('status', '?')}` | version: `{m.get('version', '?')}`")
        lines.append(f"- path: `{m['_path']}`")
        lines.append(f"- purpose: {m.get('purpose', '')}")
        lines.append(f"- ports: {', '.join(m.get('ports', [])) or '-'}")
        deps = m.get("depends_on", [])
        lines.append(f"- depends on: {', '.join(deps) if deps else '(independent)'}")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    manifests = load_manifests()
    graph = build_graph(manifests)
    (SANDBOX / "graph.json").write_text(
        json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
    (SANDBOX / "CATALOG.md").write_text(render_catalog(manifests), encoding="utf-8")
    print(f"OK: catalog built from {len(manifests)} organ(s) -> CATALOG.md, graph.json")


if __name__ == "__main__":
    main()
