import pandas as pd

from modules.decision_clarity_ui import (
    DECISION_CLARITY_CONTRACT,
    build_context_strip,
    build_decision_card,
    interview_demo_steps,
)


def _assumptions(currency="INR"):
    return {
        "category": "Packaging Procurement",
        "commodity": "Flexible Laminates",
        "procurement_intelligence_scenario": "Base",
        "display_currency": currency,
        "fx_rate": 83.0,
        "data_source": "Controlled demo data",
        "annual_volume": 500000,
        "annual_volume_unit": "kg",
    }


def _rows():
    return [
        {
            "Supplier": "Precision Flexibles Ltd",
            "technical_eligible": True,
            "Quoted Unit Price USD": 2.05,
            "adjusted_tco_unit_usd": 2.18,
            "risk_category": "Medium",
            "risk_score": 78,
        },
        {
            "Supplier": "BarrierPack Films",
            "technical_eligible": True,
            "Quoted Unit Price USD": 2.173,
            "adjusted_tco_unit_usd": 2.24,
            "risk_category": "Low",
            "risk_score": 84,
        },
    ]


def test_contract_is_versioned():
    assert DECISION_CLARITY_CONTRACT == "AIPC-UX-DECISION-CLARITY-1.0"


def test_context_strip_contains_required_business_context():
    strip = dict(build_context_strip(_assumptions()))
    assert strip["Category"] == "Packaging Procurement"
    assert strip["Commodity"] == "Flexible Laminates"
    assert strip["Scenario"] == "Base"
    assert strip["Currency"] == "INR"
    assert strip["FX rate"] == "83.00 INR/USD"
    assert strip["Data source"] == "Controlled demo data"
    assert strip["Decision status"] == "Human review required"


def test_usd_context_does_not_present_fx_as_required():
    strip = dict(build_context_strip(_assumptions("USD")))
    assert strip["Currency"] == "USD"
    assert strip["FX rate"] == "Not required"


def test_decision_card_uses_existing_ranked_result_and_display_currency():
    card = build_decision_card(_rows(), _assumptions(), confidence=86)
    assert card["supplier"] == "Precision Flexibles Ltd"
    assert card["eligibility"] == "Eligible"
    assert "170.15" in card["quote"]
    assert "180.94" in card["tco"]
    assert card["risk"] == "Medium (78/100)"
    assert card["confidence"] == "86/100"
    assert "approval" in card["approval"].lower()


def test_decision_card_never_creates_a_result_when_no_rows_exist():
    card = build_decision_card([], _assumptions(), confidence=None)
    assert card["supplier"] == "No result available"
    assert card["quote"] == "Not available"
    assert card["tco"] == "Not available"
    assert card["confidence"] == "Pending"


def test_ineligible_result_produces_fail_closed_action_language():
    rows = _rows()
    rows[0]["technical_eligible"] = False
    card = build_decision_card(rows, _assumptions(), confidence=60)
    assert card["eligibility"] == "Ineligible"
    assert "Do not progress to award" in card["action"]


def test_demo_path_is_bounded_and_ends_with_human_approval():
    steps = interview_demo_steps()
    assert 5 <= len(steps) <= 8
    assert "SourceMate" in " ".join(steps)
    assert "human procurement approval remains mandatory" in steps[-1]


def test_builder_accepts_dataframe_records_without_mutating_business_data():
    frame = pd.DataFrame(_rows())
    before = frame.copy(deep=True)
    card = build_decision_card(frame.to_dict("records"), _assumptions(), confidence=90)
    assert card["supplier"] == "Precision Flexibles Ltd"
    pd.testing.assert_frame_equal(frame, before)
