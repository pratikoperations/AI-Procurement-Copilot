"""Focused tests for the final C1 Kraft Paper UX corrections."""

from modules.c1_ux import CATEGORY_INTELLIGENCE_METRIC_CSS, technical_eligibility_label
from modules.dashboard import build_supplier_snapshot_display
from modules.data_loader import get_demo_data
from modules.scoring import enrich_supplier_scores
from modules.supplier_comparison import build_supplier_intelligence


def _assumptions(commodity="Kraft Paper"):
    return {
        "category": "Raw Material Procurement",
        "commodity": commodity,
        "annual_volume": 100000,
        "annual_volume_unit": "kg",
        "raw_material_shock": 0.0,
        "freight_shock": 0.0,
        "demand_change": 0.0,
        "display_currency": "Both",
        "fx_rate": 83,
        "category_profile": {"unit": "kg"},
    }


def test_supplier_snapshot_exposes_executive_readable_technical_eligibility():
    assumptions = _assumptions()
    scored = enrich_supplier_scores(get_demo_data("Raw Material Procurement", "Kraft Paper"), assumptions)
    display = build_supplier_snapshot_display(scored, assumptions)

    assert "Technical Eligibility" in display.columns
    assert set(display["Technical Eligibility"]) <= {"Eligible", "Ineligible", "Not assessed"}
    assert display["Technical Eligibility"].eq("Eligible").all()


def test_supplier_comparison_exposes_technical_eligibility():
    assumptions = _assumptions()
    scored = enrich_supplier_scores(get_demo_data("Raw Material Procurement", "Kraft Paper"), assumptions)
    comparison = build_supplier_intelligence(scored, "Raw Material Procurement", "Kraft Paper")["comparison_df"]

    assert "Technical Eligibility" in comparison.columns
    assert comparison["Technical Eligibility"].eq("Eligible").all()


def test_category_metric_override_is_scoped_and_does_not_change_category_data():
    assert '[data-testid="stExpander"] [data-testid="stMetricValue"]' in CATEGORY_INTELLIGENCE_METRIC_CSS
    assert "Raw Material Procurement" not in CATEGORY_INTELLIGENCE_METRIC_CSS
    assert technical_eligibility_label(True) == "Eligible"
    assert technical_eligibility_label(False) == "Ineligible"


def test_non_kraft_raw_material_retains_visible_eligibility_without_category_drift():
    assumptions = _assumptions("PET Resin")
    scored = enrich_supplier_scores(get_demo_data("Raw Material Procurement", "PET Resin"), assumptions)
    display = build_supplier_snapshot_display(scored, assumptions)

    assert assumptions["category"] == "Raw Material Procurement"
    assert assumptions["commodity"] == "PET Resin"
    assert "Technical Eligibility" in display.columns
    assert display["Technical Eligibility"].eq("Eligible").all()
