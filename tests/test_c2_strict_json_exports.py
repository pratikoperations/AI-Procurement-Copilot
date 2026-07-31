import json
import math

import numpy as np
import pandas as pd

from modules.exports import build_c2_export_manifest, build_decision_package_json


def _contains_non_finite(value):
    if isinstance(value, dict):
        return any(_contains_non_finite(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_non_finite(item) for item in value)
    if isinstance(value, float):
        return not math.isfinite(value)
    return False


def _fixtures():
    scored = pd.DataFrame(
        [
            {
                "Supplier": "Supplier A",
                "Laminate Structure": "PET / PE",
                "technical_eligible": True,
                "adjusted_tco_unit_usd": 2.75,
            }
        ]
    )
    standard = pd.DataFrame([{"Supplier": "Supplier A", "Allocation %": 100.0}])
    optimized = pd.DataFrame([{"Supplier": "Supplier A", "Allocation %": 100.0}])
    scenarios = pd.DataFrame(
        [
            {
                "Scenario": "Base Case",
                "Winning Supplier": "Supplier A",
                "Annual TCO (USD)": 1375000.0,
                "Scenario Status / Reason": "Applicable",
                "Scenario Assumption Version": "C2.5-SCENARIO-v1",
            },
            {
                "Scenario": "MetPET Availability Stress",
                "Winning Supplier": "Not applicable",
                "Annual TCO (USD)": np.nan,
                "Scenario Status / Reason": "Not applicable",
                "Scenario Assumption Version": "C2.5-SCENARIO-v1",
            },
        ]
    )
    return scored, standard, optimized, scenarios


def test_manifest_normalizes_non_finite_values_to_none():
    scored, standard, optimized, scenarios = _fixtures()
    scenarios.loc[0, "Annual TCO (USD)"] = np.inf
    manifest = build_c2_export_manifest(scored, standard, optimized, scenarios)
    assert manifest["scenarios"][0]["Annual TCO (USD)"] is None
    assert manifest["scenarios"][1]["Annual TCO (USD)"] is None
    assert not _contains_non_finite(manifest)


def test_c2_json_is_strict_and_uses_null_for_non_applicable_values():
    scored, standard, optimized, scenarios = _fixtures()
    manifest = build_c2_export_manifest(scored, standard, optimized, scenarios)
    package = build_decision_package_json(
        scored.iloc[0],
        {"estimated_ebitda_opportunity_usd": np.nan},
        standard,
        scenarios,
        {"annual_saving_usd": -np.inf},
        {"status": "Human Review Required"},
        c2_manifest=manifest,
    )
    text = package.decode("utf-8")
    assert "NaN" not in text
    assert "Infinity" not in text
    payload = json.loads(text, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
    governance = payload["flexible_laminates_governance"]
    non_applicable = next(row for row in governance["scenarios"] if row["Winning Supplier"] == "Not applicable")
    assert non_applicable["Annual TCO (USD)"] is None
    assert payload["value_metrics"]["estimated_ebitda_opportunity_usd"] is None
    assert payload["negotiation"]["annual_saving_usd"] is None


def test_non_c2_json_remains_without_governance_block_and_is_strict():
    package = build_decision_package_json(
        {"Supplier": "Supplier A", "score": np.nan},
        {},
        pd.DataFrame(),
        pd.DataFrame(),
        {},
        {"status": "Human Review Required"},
    )
    text = package.decode("utf-8")
    assert "NaN" not in text
    assert "Infinity" not in text
    payload = json.loads(text, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
    assert "flexible_laminates_governance" not in payload
    assert payload["recommended_supplier"]["score"] is None
