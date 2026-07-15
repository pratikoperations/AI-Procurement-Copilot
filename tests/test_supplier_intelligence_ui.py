"""Executive-readable Supplier Intelligence UI contract tests."""

from pathlib import Path

import pytest

from modules.supplier_intelligence_ui import (
    _resolve_supplier_profile,
    _supplier_report_filename,
    _valid_supplier_profiles,
)
from modules.ui_components import build_readable_supplier_report, format_display_value, humanize_label


ROOT = Path(__file__).resolve().parents[1]


def _profile(name, score=80):
    return {
        "supplier_name": name,
        "overall_supplier360_score": score,
        "performance": {"overall_supplier_performance_score": score - 1},
        "financial": {"assessment_status": "Assessed", "displayed_financial_score": score - 2},
        "esg": {"esg_maturity_level": "Scaling", "displayed_esg_score": score - 3},
        "innovation": {"innovation_maturity_level": "Developing", "displayed_innovation_score": score - 4},
        "srm": {"srm_classification": "Strategic", "strategic_index": score - 5},
        "risk_score": score - 6,
    }


def test_humanize_label_removes_snake_case():
    assert humanize_label("financial_stability_score") == "Financial Stability Score"
    assert "_" not in humanize_label("srm_classification")


def test_format_display_value_preserves_string_values():
    assert format_display_value("Raw Material Procurement") == "Raw Material Procurement"
    assert format_display_value("PET Resin") == "PET Resin"


def test_format_display_value_joins_collections_only():
    assert format_display_value(["Packaging Procurement", "Raw Material Procurement"]) == "Packaging Procurement, Raw Material Procurement"
    assert format_display_value(("PET Resin", "HDPE")) == "PET Resin, HDPE"
    assert format_display_value(None) == "Not provided"


def test_supplier_ui_does_not_join_scalar_profile_strings():
    source = (ROOT / "modules" / "supplier_intelligence_ui.py").read_text(encoding="utf-8")
    assert '", ".join(map(str, profile.get("approved_categories"' not in source
    assert '", ".join(map(str, profile.get("commodity_coverage"' not in source
    assert 'format_display_value(profile.get("approved_categories"))' in source
    assert 'format_display_value(profile.get("commodity_coverage"))' in source


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


def test_unique_supplier_names_preserve_profile_order():
    profile_map, warnings = _valid_supplier_profiles([
        _profile("Supplier A"),
        _profile("Supplier B"),
    ])

    assert list(profile_map) == ["Supplier A", "Supplier B"]
    assert warnings == []


def test_duplicate_supplier_names_are_deduplicated_deterministically():
    first = _profile("Supplier A", 90)
    second = _profile("Supplier A", 50)

    profile_map, warnings = _valid_supplier_profiles([first, second])

    assert list(profile_map) == ["Supplier A"]
    assert profile_map["Supplier A"] is first
    assert warnings == [
        "Duplicate supplier profile 'Supplier A' was ignored; the first profile is displayed."
    ]


def test_blank_invalid_and_empty_profiles_are_handled_safely():
    profile_map, warnings = _valid_supplier_profiles([
        {},
        {"supplier_name": "   "},
        None,
    ])

    assert profile_map == {}
    assert len(warnings) == 3

    empty_map, empty_warnings = _valid_supplier_profiles([])
    assert empty_map == {}
    assert empty_warnings == []


def test_single_supplier_profile_is_supported():
    only = _profile("Only Supplier")
    profile_map, warnings = _valid_supplier_profiles([only])

    assert list(profile_map) == ["Only Supplier"]
    assert profile_map["Only Supplier"] is only
    assert warnings == []


def test_selected_profile_resolution_uses_requested_supplier():
    profiles = [_profile("Supplier A", 90), _profile("Supplier B", 70)]

    selected, warnings = _resolve_supplier_profile(profiles, "Supplier B")

    assert selected["supplier_name"] == "Supplier B"
    assert selected["overall_supplier360_score"] == 70
    assert warnings == []


def test_selected_profile_resolution_rejects_unknown_supplier():
    with pytest.raises(KeyError, match="Supplier profile not found"):
        _resolve_supplier_profile([_profile("Supplier A")], "Missing Supplier")


def test_selected_supplier_report_filename_is_sanitized():
    assert _supplier_report_filename("ACME / India Pvt. Ltd.") == "acme_india_pvt_ltd_supplier360_report.txt"
    assert _supplier_report_filename("  ") == "supplier_supplier360_report.txt"


def test_selected_supplier_report_content_matches_profile():
    profile = _profile("Supplier B", 77)

    report = build_readable_supplier_report(profile)

    assert "Supplier: Supplier B" in report
    assert "Supplier 360 score: 77/100" in report


def test_selector_is_rendered_before_comparison_sections():
    source = (ROOT / "modules" / "supplier_intelligence_ui.py").read_text(encoding="utf-8")

    selector_position = source.index('st.selectbox("Select Supplier 360 Profile"')
    comparison_position = source.index('render_comparison_matrix(comparison, "Executive supplier comparison")')
    recommendation_position = source.index('render_comparison_matrix(recommendations, "Recommendation rankings")')

    assert selector_position < comparison_position
    assert selector_position < recommendation_position


def test_selected_supplier_heading_and_portfolio_narrative_label_are_present():
    source = (ROOT / "modules" / "supplier_intelligence_ui.py").read_text(encoding="utf-8")

    assert "Viewing Supplier 360 Profile: {selected}" in source
    assert '"Portfolio-level supplier narrative"' in source
    assert '"Executive supplier narrative"' not in source
