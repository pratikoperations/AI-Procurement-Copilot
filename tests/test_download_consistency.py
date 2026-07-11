import pandas as pd

from modules.executive_outputs import generate_executive_memo, generate_supplier_email


def _scored():
    return pd.DataFrame([{
        "Supplier":"A",
        "Quoted Unit Price USD":1.0,
        "annual_tco_usd":1000,
        "risk_category":"Low",
        "risk_score":80,
        "failure_probability":0.1,
        "risk_penalty_usd":0.01,
    }])


def test_blocked_memo_withholds_award_language():
    allocation = pd.DataFrame([{"Supplier":"A","Recommended Allocation %":100,"Role":"Primary"}])
    memo = generate_executive_memo(
        _scored(), allocation,
        {"market_quote_gap_usd":0,"negotiation_headroom_usd":0,"estimated_ebitda_opportunity_usd":0},
        80,
        {"status":"Blocked","reason":"Mixed currency","failed_checks":["Mixed currency"],"required_remediation":["Normalize currency"]},
        {"data_confidence_score":60,"confidence_category":"Limited Confidence"},
    )
    assert memo.startswith("FINAL AWARD RECOMMENDATION WITHHELD")
    assert "Award to A" not in memo
    assert "Normalize currency" in memo


def test_blocked_email_and_memo_share_status():
    eligibility = {"status":"Blocked","reason":"Mixed currency","failed_checks":["Mixed currency"],"required_remediation":[]}
    email = generate_supplier_email(_scored().iloc[0], 1.0, 500000, "Raw Material Procurement", "PET Resin", "kg", eligibility)
    assert "Current validation status: Blocked" in email
    assert "evaluation is paused" in email.lower()
