"""Build 0.9.6 data-confidence tests."""

import pandas as pd

from modules.data_confidence import calculate_data_confidence


def _complete_df():
    return pd.DataFrame([{ 
        "Supplier":"A", "Quoted Unit Price USD":1.0, "MOQ":100, "Lead Time Days":10,
        "Payment Terms":"Net 30", "Incoterms":"DDP", "Currency":"USD", "Unit":"kg",
        "OTIF %":95, "Quality PPM":500, "Audit Score":85, "Complaint Rate %":1,
        "Capacity Buffer %":20, "Supplier Capacity":1000,
    }])


def test_complete_data_scores_high():
    result = calculate_data_confidence(_complete_df())
    assert result["data_confidence_score"] >= 85
    assert result["confidence_category"] == "High Confidence"


def test_defaults_and_missing_data_reduce_confidence():
    df = _complete_df().drop(columns=["Currency", "Unit", "Supplier Capacity"])
    result = calculate_data_confidence(df, defaulted_fields=["Country", "Contract Status", "Audit Status"])
    assert result["data_confidence_score"] < 85
    assert result["defaulted_data_percentage"] > 0


def test_no_data_is_insufficient():
    result = calculate_data_confidence(pd.DataFrame())
    assert result["data_confidence_score"] == 0
    assert result["confidence_category"] == "Insufficient Data"
    assert "not the probability" in result["explanation"].lower()
