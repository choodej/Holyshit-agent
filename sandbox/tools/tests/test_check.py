from __future__ import annotations

from tools.check import check_steps


def test_check_gate_runs_expected_guards_in_order():
    labels = [label for label, _command in check_steps()]

    assert labels == [
        "tests",
        "doc lint",
        "manifest validation",
        "strict graph",
        "generated graph drift",
    ]
