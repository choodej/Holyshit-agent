"""Shadow-detection tests for graphify (pure functions, no filesystem)."""
from __future__ import annotations

from tools.graphify import (
    build_graph,
    detect_cycles,
    detect_dangling,
    detect_data_overlap,
    detect_shadows,
    detect_unguarded_writes,
    manifest_phase,
    render_catalog,
    render_mermaid,
)


def test_detects_circular_dependency():
    manifests = [
        {"organ": "a", "depends_on": ["b"]},
        {"organ": "b", "depends_on": ["a"]},
    ]
    warnings = detect_cycles(manifests)
    assert any("circular dependency" in w for w in warnings)


def test_no_cycle_for_acyclic_graph():
    manifests = [
        {"organ": "a", "depends_on": ["b"]},
        {"organ": "b", "depends_on": []},
    ]
    assert detect_cycles(manifests) == []


def test_detects_dangling_dependency():
    manifests = [{"organ": "a", "depends_on": ["ghost"]}]
    warnings = detect_dangling(manifests)
    assert any("ghost" in w for w in warnings)


def test_detects_data_overlap():
    manifests = [
        {"organ": "a", "owns_data": ["members.jsonl"]},
        {"organ": "b", "owns_data": ["Members.jsonl"]},  # case-insensitive
    ]
    warnings = detect_data_overlap(manifests)
    assert any("data overlap" in w for w in warnings)


def test_detects_unguarded_external_write():
    manifests = [{"organ": "a", "external_writes": True}]
    assert detect_unguarded_writes(manifests)
    manifests2 = [{"organ": "a", "external_writes": True, "safety_gate": True}]
    assert detect_unguarded_writes(manifests2) == []


def test_clean_system_has_no_shadows():
    manifests = [
        {"organ": "a", "depends_on": [], "owns_data": ["a.jsonl"]},
        {"organ": "b", "depends_on": ["a"], "owns_data": ["b.jsonl"]},
    ]
    assert detect_shadows(manifests) == []


def test_graph_and_mermaid_render():
    manifests = [{
        "organ": "a", "phase": "contracts", "status": "ok", "depends_on": ["b"],
        "adapters": {"Logger": ["jsonl_logger"]},
    }, {"organ": "b"}]
    g = build_graph(manifests)
    assert {"from": "a", "to": "b"} in g["edges"]
    assert g["nodes"][0]["phase"] == "contracts"
    mmd = render_mermaid(manifests)
    assert "graph TD" in mmd
    assert "contracts" in mmd
    assert "jsonl_logger" in mmd


def test_catalog_reports_phase_counts():
    manifests = [
        {"organ": "a", "phase": "contracts", "depends_on": []},
        {"organ": "b", "phase": "slice-proven", "depends_on": []},
    ]
    catalog = render_catalog(manifests, [])
    assert "## Phases" in catalog
    assert "`contracts`: 1" in catalog
    assert "`slice-proven`: 1" in catalog


def test_manifest_phase_falls_back_to_status_for_old_manifests():
    assert manifest_phase({"status": "legacy"}) == "legacy"
