from __future__ import annotations

from pathlib import Path

from tools.doc_lint import (
    CANONICAL_RULES,
    CHECK_GATE,
    DECISION_GATE,
    DOC_CONTRACT_FIELDS,
    ROUTING_DOCS,
    lint_docs,
)


def _write_docs(root: Path, *, agents_extra: str = "", examples_extra: str = "") -> None:
    for rel_path in ROUTING_DOCS:
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"# {rel_path}\n\nRoute to RULES.md {DECISION_GATE}.\n\nRun `{CHECK_GATE}`.\n",
            encoding="utf-8",
        )

    fields = "\n".join(f"- {field} ok" for field in DOC_CONTRACT_FIELDS)
    (root / "AGENTS.md").write_text(
        "# AGENTS.md\n\n"
        "Do not create a second source of truth.\n\n"
        f"{fields}\n\n"
        f"Route to RULES.md {DECISION_GATE}.\n\n"
        f"Run `{CHECK_GATE}`.\n"
        f"{agents_extra}",
        encoding="utf-8",
    )
    (root / "ANTI_DRIFT_EXAMPLES.md").write_text(
        "# ANTI_DRIFT_EXAMPLES.md\n\n"
        f"Route to RULES.md {DECISION_GATE}.\n\n"
        f"Run `{CHECK_GATE}`.\n\n"
        "## หลงทาง\n\nBad example.\n\n"
        "## ถูกทาง\n\nGood example.\n"
        f"{examples_extra}",
        encoding="utf-8",
    )
    rules = root / CANONICAL_RULES
    rules.parent.mkdir(parents=True, exist_ok=True)
    rules.write_text("# RULES.md\n\n## 10. Human Decision Gate\n", encoding="utf-8")


def test_accepts_routing_docs_with_contract_and_check_gate(tmp_path):
    _write_docs(tmp_path)
    assert lint_docs(tmp_path) == []


def test_rejects_missing_doc_contract_field(tmp_path):
    _write_docs(tmp_path)
    text = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text(
        text.replace("- **Authority:** ok\n", ""), encoding="utf-8"
    )

    errors = lint_docs(tmp_path)

    assert any("**Authority:**" in error for error in errors)


def test_rejects_doc_that_does_not_route_to_rules(tmp_path):
    _write_docs(tmp_path)
    (tmp_path / "CLAUDE.md").write_text(
        f"# CLAUDE.md\n\nRun `{CHECK_GATE}`.\n", encoding="utf-8"
    )

    errors = lint_docs(tmp_path)

    assert any("CLAUDE.md" in error and "RULES.md" in error for error in errors)


def test_rejects_doc_that_does_not_route_major_decisions_to_rule_10(tmp_path):
    _write_docs(tmp_path)
    (tmp_path / "CLAUDE.md").write_text(
        f"# CLAUDE.md\n\nRoute to RULES.md.\n\nRun `{CHECK_GATE}`.\n", encoding="utf-8"
    )

    errors = lint_docs(tmp_path)

    assert any("CLAUDE.md" in error and "§10" in error for error in errors)


def test_rejects_missing_canonical_human_decision_gate(tmp_path):
    _write_docs(tmp_path)
    (tmp_path / CANONICAL_RULES).write_text("# RULES.md\n", encoding="utf-8")

    errors = lint_docs(tmp_path)

    assert any("Human Decision Gate" in error for error in errors)


def test_live_docs_pass_doc_lint():
    assert lint_docs() == []
