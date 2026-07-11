"""Executive-readable Supplier Intelligence UI contract tests."""

from pathlib import Path

from modules.ui_components import build_readable_supplier_report, humanize_label


ROOT = Path(__file__).resolve().parents[1]


def test_humanize_label_removes_snake_case():
    assert humanize_label("financial_stability_score") == "Financial Stability Score"
    assert "_" not in humanize_label("srm_classification")


def test_readable_report_contains_business_labels_not_payload_syntax():
    profile = {
        "supplier_name": "Supplier A",
        "overall_supplier360_score": 72,
        "performance": {"overall_supplier_performance_score": 75, "performance_category": "Strong"},
        "financial": {"assessment_status": "Insufficient Data", "displayed_financial_score": 50},
        "esg": {"esg_maturity_level": "Basic", "displayed_esg_score": 50},
        "innovation": {"innovation_maturity_level": "Basic", "displayed_innovation_score": 50},
        "srm": {"srm_classification": "Approved"},
    }
    report = build_readable_supplier_report(profile)
    assert "Supplier 360 score" in report
    assert "Financial assessment" in report
    assert "financial_stability_score" not in report
    assert "{" not in report
    assert "}" not in report


def test_supplier_ui_uses_charts_cards_and_matrices():
    source = (ROOT / "modules" / "supplier_intelligence_ui.py").read_text(encoding="utf-8")
    for helper in [
        "render_dimension_chart",
        "render_score_matrix",
        "render_key_value_matrix",
        "render_action_plan",
        "render_comparison_matrix",
    ]:
        assert helper in source
    assert "st.json(" not in source


def test_ui_component_scores_are_bounded_in_source_contract():
    source = (ROOT / "modules" / "ui_components.py").read_text(encoding="utf-8")
    assert "min(100" in source
    assert "st.progress" in source
    assert "st.plotly_chart" in source
