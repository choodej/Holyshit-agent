"""graphify — generate "สารบัญ" ของระบบจาก manifest.json ของทุกอวัยวะ อัตโนมัติ

กฎ: สารบัญ/กราฟต้องสร้างจากโค้ดเท่านั้น ห้ามเขียนมือ -> ไม่มีทางตกขบวน
ผลลัพธ์:
  - sandbox/CATALOG.md   (อ่านง่ายสำหรับคน)
  - sandbox/graph.json   (สำหรับเครื่อง/เครื่องมือต่อ)

รัน: python tools/build_graph.py
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


def render_catalog(manifests: list[dict], graph: dict) -> str:
    lines = ["# CATALOG — สารบัญระบบ (auto-generated, ห้ามแก้มือ)", ""]
    lines.append(f"อวัยวะทั้งหมด: {len(manifests)}")
    lines.append("")
    for m in manifests:
        lines.append(f"## {m['organ']} — {m.get('title', '')}")
        lines.append(f"- สถานะ: `{m.get('status', '?')}`  | เวอร์ชัน: `{m.get('version', '?')}`")
        lines.append(f"- ที่อยู่: `{m['_path']}`")
        lines.append(f"- หน้าที่: {m.get('purpose', '')}")
        lines.append(f"- ports: {', '.join(m.get('ports', [])) or '-'}")
        deps = m.get("depends_on", [])
        lines.append(f"- ขึ้นกับ: {', '.join(deps) if deps else '(อิสระ)'}")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    manifests = load_manifests()
    graph = build_graph(manifests)
    (SANDBOX / "graph.json").write_text(
        json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
    (SANDBOX / "CATALOG.md").write_text(
        render_catalog(manifests, graph), encoding="utf-8")
    print(f"✅ สร้างสารบัญจาก {len(manifests)} อวัยวะ -> CATALOG.md, graph.json")


if __name__ == "__main__":
    main()
