"""Regression contracts for Build S1.4 deterministic export caching."""

import json

import pandas as pd

from modules import exports


def _sample_scored_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Supplier": ["Atlas", "Beacon"],
            "Quoted Unit Price USD": [1.10, 1.20],
            "adjusted_tco_unit_usd": [1.15, 1.25],
            "annual_tco_usd": [1150.0, 1250.0],
            "risk_score": [80.0, 75.0],
            "risk_category": ["Low", "Medium"],
            "performance_score": [82.0, 78.0],
            "esg_score": [70.0, 72.0],
            "total_score": [79.0, 76.0],
        }
    )


def test_expensive_export_builders_use_bounded_streamlit_cache() -> None:
    cached_builders = (
        exports.build_readable_supplier_scores,
        exports.build_readable_supplier_comparison,
        exports.build_readable_allocation,
        exports.build_readable_should_cost,
        exports.build_readable_scenarios,
        exports.build_decision_package_json,
        exports.build_excel_workbook,
    )

    assert exports.EXPORT_CACHE_MAX_ENTRIES == 16
    for builder in cached_builders:
        assert callable(builder)
        assert hasattr(builder, "clear")


def test_cached_readable_scores_are_value_stable_and_isolated() -> None:
    exports.build_readable_supplier_scores.clear()
    scored = _sample_scored_frame()
    confidence = {"data_confidence_score": 88, "confidence_category": "High"}
    eligibility = {"status": "Eligible", "reason": "Checks passed"}

    first = exports.build_readable_supplier_scores(
        scored,
        confidence,
        eligibility,
        display_currency="USD",
        fx_rate=83,
        annual_volume=1000,
        annual_volume_unit="units",
    )
    second = exports.build_readable_supplier_scores(
        scored,
        confidence,
        eligibility,
        display_currency="USD",
        fx_rate=83,
        annual_volume=1000,
        annual_volume_unit="units",
    )

    pd.testing.assert_frame_equal(first, second)
    first.loc[0, "Supplier"] = "Mutated locally"
    assert second.loc[0, "Supplier"] == "Atlas"


def test_cached_json_package_preserves_exact_business_payload() -> None:
    exports.build_decision_package_json.clear()
    scored = _sample_scored_frame()
    allocation = pd.DataFrame({"Supplier": ["Atlas"], "Allocation %": [100.0]})
    scenarios = pd.DataFrame({"Scenario": ["Base"], "Annual TCO USD": [1150.0]})

    payload_bytes = exports.build_decision_package_json(
        scored.iloc[0],
        {"estimated_ebitda_opportunity_usd": 50.0},
        allocation,
        scenarios,
        {"annual_saving_usd": 25.0},
        {"status": "Eligible"},
    )
    payload = json.loads(payload_bytes.decode("utf-8"))

    assert payload["recommended_supplier"]["Supplier"] == "Atlas"
    assert payload["value_metrics"]["estimated_ebitda_opportunity_usd"] == 50.0
    assert payload["allocation"] == [{"Supplier": "Atlas", "Allocation %": 100.0}]
    assert payload["scenarios"] == [{"Scenario": "Base", "Annual TCO USD": 1150.0}]
    assert payload["negotiation"]["annual_saving_usd"] == 25.0
    assert payload["eligibility"]["status"] == "Eligible"
