"""Read-only Governed Calculation Explorer and SourceMate Basic View."""
from __future__ import annotations

from dataclasses import asdict

import streamlit as st

from modules.calculation_explorer_adapter import build_explorer_payload
from modules.calculation_explorer_currency_ui import render_currency_aware_calculation_explorer
from modules.calculation_explorer_presenter import build_governed_explorer_presentation
from modules.calculation_reconciliation_gate3 import reconcile_trace
from modules.calculation_trace_adapters import build_should_cost_trace
from modules.config import DEFAULT_FX_RATE
from modules.data_loader import get_demo_suppliers
from modules.flexible_laminate_cost import calculate_flexible_laminate_should_cost
from modules.raw_material_cost import calculate_raw_material_should_cost
from modules.should_cost import calculate_packaging_should_cost
from modules.steel_cost import calculate_steel_should_cost
from modules.tco import calculate_supplier_tco

st.set_page_config(page_title="Governed Calculation Explorer", page_icon="🔎", layout="wide")

STEEL_INPUTS = {
    "annual_volume_kg": 500000,
    "base_steel_usd_per_kg": 0.72,
    "profile_premium_usd_per_kg": 0.05,
    "rolling_conversion_usd_per_kg": 0.10,
    "zinc_cost_usd_per_kg": 0.0,
    "paint_treatment_usd_per_kg": 0.0,
    "energy_surcharge_usd_per_kg": 0.04,
    "yield_pct": 96.0,
    "slitting_cutting_usd_per_kg": 0.025,
    "packing_usd_per_kg": 0.015,
    "freight_usd_per_kg": 0.045,
    "sourcing_route": "Domestic",
    "import_duty_pct": 0.0,
    "supplier_margin_pct": 8.0,
}

ROUTES = {
    "PET Resin should-cost": {
        "calculation_id": "PET-001",
        "formula_id": "F-RM-SHOULDCOST",
        "coverage_id": "REC-PET",
        "category": "PET Resin",
        "service": "calculate_raw_material_should_cost:PET",
    },
    "Kraft Paper should-cost": {
        "calculation_id": "KRF-001",
        "formula_id": "F-RM-SHOULDCOST",
        "coverage_id": "REC-KRF",
        "category": "Kraft Paper",
        "service": "calculate_raw_material_should_cost:Kraft",
    },
    "Corrugated Board should-cost": {
        "calculation_id": "COR-001",
        "formula_id": "F-PKG-SHOULDCOST",
        "coverage_id": "REC-COR",
        "category": "Corrugated Board",
        "service": "calculate_packaging_should_cost",
    },
    "Flexible Laminates should-cost": {
        "calculation_id": "LAM-004",
        "formula_id": "F-C2-SHOULDCOST",
        "coverage_id": "REC-LAM",
        "category": "Flexible Laminates",
        "service": "calculate_flexible_laminate_should_cost",
    },
    "Steel should-cost": {
        "calculation_id": "STL-003",
        "formula_id": "F-C3-SHOULDCOST",
        "coverage_id": "REC-STL",
        "category": "Steel",
        "service": "calculate_steel_should_cost",
    },
    "Packaging TCO — deferred adapter example": {
        "calculation_id": "TCO-001",
        "formula_id": "F-TCO-PKG",
        "coverage_id": "REC-TCO-PKG",
        "category": "Packaging",
        "service": "calculate_supplier_tco",
    },
}


def _authoritative_output(route_name: str):
    if route_name == "PET Resin should-cost":
        return calculate_raw_material_should_cost("PET Resin")
    if route_name == "Kraft Paper should-cost":
        return calculate_raw_material_should_cost("Kraft Paper")
    if route_name == "Corrugated Board should-cost":
        return calculate_packaging_should_cost()
    if route_name == "Flexible Laminates should-cost":
        return calculate_flexible_laminate_should_cost()
    if route_name == "Steel should-cost":
        return calculate_steel_should_cost("CR_COIL_COMMERCIAL", **STEEL_INPUTS)
    supplier = get_demo_suppliers().iloc[0].to_dict()
    return calculate_supplier_tco(supplier, 500000)


st.title("Governed Calculation Explorer")
st.caption("Basic Interview Version — read-only explanation, provenance, trace, reconciliation, evidence and human-review boundaries.")
st.warning(
    "Formula metadata is documentation only. Existing authoritative services produce business results. "
    "Evidence references do not prove external verification. Human approval remains mandatory."
)
route_name = st.selectbox(
    "Select a controlled demonstration route",
    tuple(ROUTES),
    help="This selects an existing authoritative route; it does not edit assumptions or calculations.",
)

currency_columns = st.columns(2)
display_currency = currency_columns[0].radio(
    "Explorer Display Currency",
    ("USD", "INR", "Both"),
    index=1,
    horizontal=True,
    help="Display-only selection. Canonical calculations remain in USD.",
)
fx_rate = currency_columns[1].number_input(
    "USD-INR FX Rate",
    min_value=60.0,
    max_value=150.0,
    value=float(DEFAULT_FX_RATE),
    step=1.0,
    help="Used only for display conversion. Trace and reconciliation remain on canonical USD values.",
)

route = ROUTES[route_name]
authoritative_output = _authoritative_output(route_name)
assumptions = {
    "category": route["category"],
    "commodity": route_name,
    "annual_volume": 500000,
    "annual_volume_unit": "kg" if route["category"] in {"PET Resin", "Kraft Paper", "Flexible Laminates", "Steel"} else "unit",
    "data_source": "Controlled portfolio demonstration",
    "display_currency": display_currency,
    "fx_rate_inr_per_usd": fx_rate,
}
explorer_payload = build_explorer_payload(
    context={
        "route": route_name,
        "mode": "read_only",
        "programme": "EAS-BIV Gate 4",
        "display_currency": display_currency,
        "fx_rate_inr_per_usd": fx_rate,
    },
    assumptions=assumptions,
    authoritative_results={route["calculation_id"]: authoritative_output},
    derived_keys=("annual_volume_unit",),
)

trace = None
reconciliation = None
if route["coverage_id"] != "REC-TCO-PKG":
    trace = build_should_cost_trace(
        calculation_id=route["calculation_id"],
        formula_id=route["formula_id"],
        category=route["category"],
        inputs={"route": route_name, "mode": "controlled demonstration"},
        authoritative_result=authoritative_output,
    )
    reconciliation = reconcile_trace(
        trace=trace,
        authoritative_service=route["service"],
        authoritative_output=authoritative_output,
        calculation_id=route["calculation_id"],
        formula_id=route["formula_id"],
        formula_version="1.0",
        compared_fields=("",),
        repeated_trace_id=trace.trace_id,
    )

presentation = build_governed_explorer_presentation(
    explorer_payload=explorer_payload,
    calculation_id=route["calculation_id"],
    coverage_id=route["coverage_id"],
    trace=None if trace is None else asdict(trace),
    reconciliation=None if reconciliation is None else asdict(reconciliation),
)
render_currency_aware_calculation_explorer(
    presentation,
    display_currency=display_currency,
    fx_rate=fx_rate,
)

st.markdown("---")
st.caption(
    "Read-only portfolio demonstration. No formula execution, no assumption editing, no autonomous award, "
    "no production allocation, no approval persistence, no external evidence retrieval, and no realized-savings claim."
)
