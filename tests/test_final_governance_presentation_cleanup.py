"""Presentation contracts for the final governance-message cleanup."""

from pathlib import Path

from modules.procurement_intelligence_ui import _split_warning_messages


def test_non_blocking_governance_disclosures_are_not_actionable_warnings() -> None:
    messages = (
        "Adapter construction is decision support only; human procurement approval remains mandatory.",
        "Allocation is decision support only; human procurement approval remains mandatory.",
        "Controlled synthetic demonstration assumption; not verified supplier evidence.",
        "Feasibility is decision support only; supplier capacity is not independently verified.",
        "Human procurement approval remains mandatory.",
        "Supplier capacity is supplied evidence and has not been independently verified.",
    )

    actionable, governance = _split_warning_messages(messages)

    assert actionable == ()
    assert governance == messages


def test_material_review_warning_remains_actionable() -> None:
    actionable, governance = _split_warning_messages(
        (
            "Feasibility is indeterminate; do not treat this result as infeasible.",
            "Human procurement approval remains mandatory.",
        )
    )

    assert actionable == ("Feasibility is indeterminate; do not treat this result as infeasible.",)
    assert governance == ("Human procurement approval remains mandatory.",)


def test_procurement_ui_keeps_errors_and_actionable_warning_styling() -> None:
    source = Path("modules/procurement_intelligence_ui.py").read_text(encoding="utf-8")

    assert 'st.error(f"Canonical allocation route is blocked: {route_status}")' in source
    assert 'st.warning("Canonical allocation route completed with review items requiring attention.")' in source
    assert 'for warning in allocation_actionable:' in source
    assert 'for warning in scenario_actionable:' in source


def test_procurement_ui_collapses_governance_evidence_and_keeps_one_approval_boundary() -> None:
    source = Path("modules/procurement_intelligence_ui.py").read_text(encoding="utf-8")

    assert 'st.expander("Governance & Evidence Details", expanded=False)' in source
    assert 'st.write("**Human procurement approval required.**")' in source
    assert 'Canonical allocation route completed with warnings. Human procurement review is mandatory.' not in source
    assert 'Scenario allocation is available with warnings; human review is mandatory.' not in source
    assert 'for warning in optimized_allocation.get("warnings", ())' not in source
    assert 'for warning in presentation.warnings' not in source
