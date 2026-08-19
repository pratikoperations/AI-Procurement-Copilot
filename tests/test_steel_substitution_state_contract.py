"""Regression assurance for the hosted Steel substitution-state contract."""

from modules.data_loader import get_demo_data
from modules.scoring import enrich_supplier_scores


def _steel_assumptions(status: str) -> dict:
    return {
        "category": "Raw Material Procurement",
        "commodity": "Steel",
        "annual_volume": 500000.0,
        "fx_rate": 83.0,
        "display_currency": "Both",
        "steel_profile": "GI_COIL_Z120",
        "steel_substitution_status": status,
    }


def test_hosted_non_applicable_state_does_not_block_all_gi_suppliers():
    suppliers = get_demo_data(
        "Raw Material Procurement",
        "Steel",
        expanded_supplier_pool=True,
    )

    scored = enrich_supplier_scores(suppliers, _steel_assumptions("Non-applicable"))

    assert int(scored["technical_eligible"].sum()) > 0
    assert scored.attrs["steel_recommendation"]["winner"] is not None
    assert scored.attrs["steel_recommendation"]["human_approval_required"] is True
    assert scored.attrs["steel_recommendation"]["autonomous_award"] is False


def test_rejected_substitution_state_remains_fail_closed():
    suppliers = get_demo_data(
        "Raw Material Procurement",
        "Steel",
        expanded_supplier_pool=True,
    )

    scored = enrich_supplier_scores(suppliers, _steel_assumptions("Rejected"))

    assert int(scored["technical_eligible"].sum()) == 0
    assert scored.attrs["steel_recommendation"]["winner"] is None
