"""Cross-category assurance for hosted synthetic-demo analytical routing."""

from __future__ import annotations

import pandas as pd
import pytest

from modules.commodity_library import COMMODITIES, get_commodity_profile
from modules.data_loader import get_demo_data
from modules.multi_supplier_allocation_adapter import (
    AdapterStatus,
    build_multi_supplier_allocation_adapter,
)
from modules.scoring import enrich_supplier_scores


def _assumptions(category: str, commodity: str) -> dict:
    values = {
        "category": category,
        "commodity": commodity,
        "annual_volume": 500000.0,
        "annual_volume_unit": get_commodity_profile(category, commodity).get("unit", "piece"),
        "fx_rate": 83.0,
        "display_currency": "Both",
        "raw_material_shock": 0.0,
        "freight_shock": 0.0,
        "demand_change": 0.0,
        "required_awardee_count": 2,
        "minimum_awarded_share_pct": 10.0,
        "maximum_supplier_share_pct": 75.0,
        "minimum_continuity_share_pct": 15.0,
        "minimum_risk_score": 55.0,
        "minimum_esg_score": 50.0,
        "capacity_utilization_ceiling_pct": 90.0,
        "comparison_currency": "USD",
        "required_supplier_ids": (),
        "excluded_supplier_ids": (),
    }
    if commodity == "Steel":
        values.update(
            {
                "steel_profile": "CR_COIL_COMMERCIAL",
                "steel_substitution_status": "Not applicable",
            }
        )
    return values


def _demo(category: str, commodity: str) -> pd.DataFrame:
    structure = "PET / PE" if commodity == "Flexible Laminates" else None
    return get_demo_data(
        category,
        commodity,
        selected_structure=structure,
        expanded_supplier_pool=True,
    )


@pytest.mark.parametrize(
    ("category", "commodity"),
    [
        (category, commodity)
        for category, commodities in COMMODITIES.items()
        for commodity in commodities
    ],
)
def test_every_active_synthetic_commodity_reaches_allocation_adapter(category, commodity):
    assumptions = _assumptions(category, commodity)
    demo = _demo(category, commodity)
    scored = enrich_supplier_scores(demo, assumptions)

    assert not scored.empty
    assert "Supplier Capacity" in scored.columns
    assert scored["Supplier Capacity"].notna().all()
    assert (scored["Supplier Capacity"] > 0).all()

    source_type = "steel_synthetic" if commodity == "Steel" else "synthetic_demo"
    result = build_multi_supplier_allocation_adapter(
        scored,
        assumptions,
        route_name="cross-category-synthetic-assurance",
        source_type=source_type,
    )
    assert result.ready, (category, commodity, result.status_code, result.blocking_reasons)
    assert result.status_code is AdapterStatus.ADAPTER_READY


def test_generic_packaging_capacity_is_controlled_synthetic_evidence_only():
    for commodity in ("Corrugated Board", "PET Bottles", "Labels"):
        demo = _demo("Packaging Procurement", commodity)
        assert "Supplier Capacity" in demo.columns
        assert demo["Supplier Capacity"].notna().all()
        assert (demo["Supplier Capacity"] > 0).all()
        assert "Controlled synthetic demonstration capacity" in demo.attrs["capacity_evidence_basis"]


def test_uploaded_or_supplied_data_without_capacity_still_fails_closed():
    assumptions = _assumptions("Packaging Procurement", "Corrugated Board")
    scored = enrich_supplier_scores(_demo("Packaging Procurement", "Corrugated Board"), assumptions)
    supplied = scored.drop(columns=["Supplier Capacity"])

    result = build_multi_supplier_allocation_adapter(
        supplied,
        assumptions,
        route_name="uploaded-capacity-fail-closed",
        source_type="uploaded_rfq",
    )
    assert not result.ready
    assert result.status_code is AdapterStatus.MISSING_SUPPLIER_CAPACITY


def test_steel_scoring_returns_analytical_contract_without_ui_termination():
    assumptions = _assumptions("Raw Material Procurement", "Steel")
    scored = enrich_supplier_scores(_demo("Raw Material Procurement", "Steel"), assumptions)

    assert scored.attrs["steel_governed_path"] is True
    assert "steel_recommendation" in scored.attrs
    for field in (
        "adjusted_tco_unit_usd",
        "total_score",
        "risk_score",
        "performance_score",
        "esg_score",
        "Supplier Capacity",
    ):
        assert field in scored.columns
