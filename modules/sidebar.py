"""Category-aware sidebar controls for the Streamlit app."""

import math

import streamlit as st

from modules.c1_ux import apply_c1_ux_overrides
from modules.category_engine import ensure_category_profile, get_category_profile
from modules.config import DEFAULT_FX_RATE, EDITION, FUTURE_CATEGORIES, SUPPORTED_CATEGORIES
from modules.rfq_integration_controller import governed_route_enabled
from modules.scenario_engine import SCENARIOS
from modules.steel_ux import render_steel_sidebar_controls
from modules.ui_theme import apply_ui_theme
from modules.unit_display import annual_volume_label, canonical_unit, quantity_basis_caption

FX_RATE_MIN = 60
FX_RATE_MAX = 150
FX_RATE_STEP = 1
LAMINATE_PRINT_PROFILE_RANGES = {
    "Unprinted": (0, 0, 0),
    "Up to 4 colours": (1, 4, 4),
    "5–8 colours": (5, 8, 5),
}
LAMINATE_PRINT_PROFILE_KEY = "c2_laminate_print_profile"
LAMINATE_COLOUR_COUNT_KEY = "c2_laminate_number_of_colours"
LAMINATE_TOOLING_STATUS_KEY = "c2_laminate_tooling_status"
LAMINATE_TOOLING_AVAILABILITY_KEY = "c2_laminate_existing_tooling_available"
LAMINATE_TOOLING_COST_KEY = "c2_laminate_tooling_cost_per_colour_usd"
LAMINATE_TOOLING_LIFETIME_KEY = "c2_laminate_tooling_lifetime_volume_kg"
LAMINATE_PRINTED_TOOLING_DEFAULTS = {
    "tooling_status": "New",
    "existing_tooling_available": "Not applicable",
    "tooling_cost_per_colour_usd": 250.0,
    "tooling_lifetime_volume_kg": 250000.0,
}
GENERIC_SCENARIO_DEFAULTS = {
    "raw_material_shock": 0.0,
    "freight_shock": 0.0,
    "demand_change": 0.0,
    "procurement_intelligence_scenario": "Base Case",
}
GENERIC_ALLOCATION_DEFAULTS = {
    "max_supplier_share": 75,
    "min_backup_share": 25,
    "min_risk_score": 55,
    "min_esg_score": 50,
}


def normalize_laminate_colour_count(print_profile, number_of_colours):
    """Return a deterministic colour count compatible with the selected profile."""
    if print_profile not in LAMINATE_PRINT_PROFILE_RANGES:
        raise ValueError(f"Unsupported print profile '{print_profile}'.")
    minimum, maximum, default = LAMINATE_PRINT_PROFILE_RANGES[print_profile]
    try:
        count = int(number_of_colours)
    except (TypeError, ValueError):
        return default
    return count if minimum <= count <= maximum else default


def normalize_laminate_tooling_state(
    print_profile,
    tooling_status,
    existing_tooling_available,
    tooling_cost_per_colour_usd,
    tooling_lifetime_volume_kg,
):
    """Return tooling state compatible with printed or unprinted laminate governance."""
    if print_profile not in LAMINATE_PRINT_PROFILE_RANGES:
        raise ValueError(f"Unsupported print profile '{print_profile}'.")
    if print_profile == "Unprinted":
        return {
            "tooling_status": "Not applicable",
            "existing_tooling_available": "Not applicable",
            "tooling_cost_per_colour_usd": 0.0,
            "tooling_lifetime_volume_kg": 0.0,
        }

    try:
        cost = float(tooling_cost_per_colour_usd)
        lifetime = float(tooling_lifetime_volume_kg)
    except (TypeError, ValueError):
        return dict(LAMINATE_PRINTED_TOOLING_DEFAULTS)
    finite_non_negative_cost = math.isfinite(cost) and cost >= 0
    finite_positive_lifetime = math.isfinite(lifetime) and lifetime > 0
    valid_new = tooling_status == "New" and existing_tooling_available == "Not applicable"
    valid_existing = tooling_status == "Existing" and existing_tooling_available in {"Yes", "No", "Not assessed"}
    if finite_non_negative_cost and finite_positive_lifetime and (valid_new or valid_existing):
        return {
            "tooling_status": tooling_status,
            "existing_tooling_available": existing_tooling_available,
            "tooling_cost_per_colour_usd": cost,
            "tooling_lifetime_volume_kg": lifetime,
        }
    return dict(LAMINATE_PRINTED_TOOLING_DEFAULTS)


def build_sidebar_result(**values):
    """Build the governed sidebar return contract with a guaranteed category profile."""
    result = dict(values)
    result["category_profile"] = ensure_category_profile(result.get("category_profile"))
    result.setdefault("annual_volume_unit", canonical_unit(result["category_profile"].get("unit", "unit")))
    return result


def _render_sourcing_setup():
    """Render the always-visible workflow-routing controls."""
    route_enabled, route_warning = governed_route_enabled()
    data_sources = ["Synthetic Demo", "Upload RFQ CSV/Excel"]
    if route_enabled:
        data_sources.append("Governed v1.3 Workbook Review Preview")
    data_source = st.sidebar.radio("Data Source", data_sources, index=0)
    if route_warning:
        st.sidebar.warning(route_warning)

    category = st.sidebar.selectbox("Category Engine", SUPPORTED_CATEGORIES, index=0)
    base_profile = ensure_category_profile(get_category_profile(category))
    commodity = st.sidebar.selectbox("Commodity / Material", base_profile["commodities"], index=0)
    category_profile = ensure_category_profile(get_category_profile(category, commodity))
    if category_profile["engine_status"] != "Active":
        st.sidebar.warning(
            "Raw-material architecture is available as a foundation preview. "
            "Full category-specific scoring is planned for Build 0.9.4."
        )
    return data_source, category, commodity, category_profile


def _render_kraft_inputs(category, commodity):
    values = {
        "kraft_variant": "Recycled Kraft",
        "kraft_gsm": 150,
        "kraft_strength_grade": "22 BF",
    }
    if category == "Raw Material Procurement" and commodity == "Kraft Paper":
        with st.sidebar.expander("Category Inputs — Kraft Paper", expanded=True):
            st.caption("Controlled synthetic profiles for portfolio demonstration; not live market specifications.")
            values["kraft_variant"] = st.selectbox("Fibre Basis", ["Recycled Kraft", "Virgin Kraft"], index=0)
            values["kraft_gsm"] = st.selectbox("GSM", [120, 150, 180], index=1)
            values["kraft_strength_grade"] = st.selectbox("Strength Grade", ["18 BF", "22 BF", "28 BF"], index=1)
            st.caption("Downstream linkage: Corrugated Board should-cost assumption review.")
    return values


def _laminate_defaults():
    return {
        "laminate_structure": "PET / PE",
        "laminate_total_micron": 70,
        "laminate_print_profile": "Up to 4 colours",
        "laminate_print_process": "Rotogravure",
        "laminate_number_of_colours": 4,
        "laminate_adhesive_type": "Solvent-free",
        "laminate_printing_loss_pct": 3.0,
        "laminate_lamination_loss_pct": 2.0,
        "laminate_slitting_loss_pct": 1.0,
        "laminate_tooling_status": "New",
        "laminate_existing_tooling_available": "Not applicable",
        "laminate_tooling_cost_per_colour_usd": 250.0,
        "laminate_tooling_lifetime_volume_kg": 250000.0,
    }


def _render_laminate_inputs(category, commodity):
    values = _laminate_defaults()
    if not (category == "Packaging Procurement" and commodity == "Flexible Laminates"):
        return values

    with st.sidebar.expander("Category Inputs — Material Specification", expanded=True):
        st.caption(
            "Controlled synthetic C2 profiles; total micron is metadata only and does not infer physical mass "
            "or an approved technical specification."
        )
        values["laminate_structure"] = st.selectbox(
            "Laminate Structure", ["PET / PE", "PET / MetPET / PE", "BOPP / CPP"], index=0
        )
        values["laminate_total_micron"] = st.number_input(
            "Total Micron (metadata only)", min_value=35, max_value=140, value=70, step=1
        )
        values["laminate_adhesive_type"] = st.selectbox(
            "Adhesive Type", ["Solvent-based", "Solvent-free"], index=1
        )

    with st.sidebar.expander("Category Inputs — Printing", expanded=False):
        values["laminate_print_profile"] = st.selectbox(
            "Print Profile",
            ["Unprinted", "Up to 4 colours", "5–8 colours"],
            index=1,
            key=LAMINATE_PRINT_PROFILE_KEY,
        )
        values["laminate_print_process"] = st.selectbox(
            "Print Process", ["Rotogravure", "Flexographic"], index=0
        )
        minimum_colours, maximum_colours, default_colours = LAMINATE_PRINT_PROFILE_RANGES[
            values["laminate_print_profile"]
        ]
        current_colours = st.session_state.get(LAMINATE_COLOUR_COUNT_KEY, default_colours)
        st.session_state[LAMINATE_COLOUR_COUNT_KEY] = normalize_laminate_colour_count(
            values["laminate_print_profile"], current_colours
        )
        values["laminate_number_of_colours"] = st.number_input(
            "Number of Colours",
            min_value=minimum_colours,
            max_value=maximum_colours,
            step=1,
            key=LAMINATE_COLOUR_COUNT_KEY,
            disabled=values["laminate_print_profile"] == "Unprinted",
        )

    with st.sidebar.expander("Category Inputs — Process Losses and Tooling", expanded=False):
        values["laminate_printing_loss_pct"] = st.number_input(
            "Printing Loss %", min_value=0.0, max_value=8.0, value=3.0, step=0.5
        )
        values["laminate_lamination_loss_pct"] = st.number_input(
            "Lamination Loss %", min_value=0.0, max_value=6.0, value=2.0, step=0.5
        )
        values["laminate_slitting_loss_pct"] = st.number_input(
            "Slitting Loss %", min_value=0.0, max_value=5.0, value=1.0, step=0.5
        )
        current_tooling = normalize_laminate_tooling_state(
            values["laminate_print_profile"],
            st.session_state.get(LAMINATE_TOOLING_STATUS_KEY, "New"),
            st.session_state.get(LAMINATE_TOOLING_AVAILABILITY_KEY, "Not applicable"),
            st.session_state.get(LAMINATE_TOOLING_COST_KEY, 250.0),
            st.session_state.get(LAMINATE_TOOLING_LIFETIME_KEY, 250000.0),
        )
        st.session_state[LAMINATE_TOOLING_STATUS_KEY] = current_tooling["tooling_status"]
        st.session_state[LAMINATE_TOOLING_AVAILABILITY_KEY] = current_tooling["existing_tooling_available"]
        st.session_state[LAMINATE_TOOLING_COST_KEY] = current_tooling["tooling_cost_per_colour_usd"]
        st.session_state[LAMINATE_TOOLING_LIFETIME_KEY] = current_tooling["tooling_lifetime_volume_kg"]
        unprinted = values["laminate_print_profile"] == "Unprinted"
        values["laminate_tooling_status"] = st.selectbox(
            "Tooling Status",
            ["New", "Existing", "Not applicable"],
            key=LAMINATE_TOOLING_STATUS_KEY,
            disabled=unprinted,
        )
        values["laminate_existing_tooling_available"] = st.selectbox(
            "Existing Tooling Available",
            ["Not applicable", "Yes", "No", "Not assessed"],
            key=LAMINATE_TOOLING_AVAILABILITY_KEY,
            disabled=unprinted,
        )
        values["laminate_tooling_cost_per_colour_usd"] = st.number_input(
            "Tooling Cost per Colour USD",
            min_value=0.0,
            step=25.0,
            key=LAMINATE_TOOLING_COST_KEY,
            disabled=unprinted,
        )
        values["laminate_tooling_lifetime_volume_kg"] = st.number_input(
            "Tooling Lifetime Volume kg",
            min_value=0.0 if unprinted else 1.0,
            step=10000.0,
            key=LAMINATE_TOOLING_LIFETIME_KEY,
            disabled=unprinted,
        )
    return values


def _render_commercial_basis(category_profile):
    annual_volume_unit = canonical_unit(category_profile.get("unit", "unit"))
    with st.sidebar.expander("Commercial Basis", expanded=False):
        annual_volume = st.number_input(
            annual_volume_label(annual_volume_unit), min_value=1000, value=500000, step=10000
        )
        st.caption(quantity_basis_caption(annual_volume, annual_volume_unit))
        fx_rate = st.slider(
            "USD-INR FX Rate",
            min_value=FX_RATE_MIN,
            max_value=FX_RATE_MAX,
            value=DEFAULT_FX_RATE,
            step=FX_RATE_STEP,
        )
        display_currency = st.radio("Display Currency", ["USD", "INR", "Both"], index=2)
    return annual_volume, annual_volume_unit, fx_rate, display_currency


def _render_generic_scenario_inputs(commodity, enabled):
    values = dict(GENERIC_SCENARIO_DEFAULTS)
    if enabled:
        with st.sidebar.expander("Scenario Inputs", expanded=False):
            values["procurement_intelligence_scenario"] = st.selectbox(
                "Procurement Intelligence Scenario",
                list(SCENARIOS.keys()),
                index=0,
            )
            shock_label = "Paper / Raw Material Shock %" if commodity == "Kraft Paper" else "Raw Material Shock %"
            values["raw_material_shock"] = st.slider(shock_label, -20, 40, 0) / 100
            values["freight_shock"] = st.slider("Freight Shock %", -20, 80, 0) / 100
            values["demand_change"] = st.slider("Demand Change %", -50, 50, 0) / 100
    return values


def _render_generic_allocation_rules(enabled):
    values = dict(GENERIC_ALLOCATION_DEFAULTS)
    if enabled:
        with st.sidebar.expander("Allocation Rules", expanded=False):
            values["max_supplier_share"] = st.slider("Max Supplier Share %", 50, 100, 75)
            values["min_backup_share"] = st.slider("Minimum Backup Share %", 0, 40, 25)
            values["min_risk_score"] = st.slider("Minimum Risk Score", 0, 100, 55)
            values["min_esg_score"] = st.slider("Minimum ESG Score", 0, 100, 50)
    return values


def _render_about_roadmap():
    with st.sidebar.expander("About / Roadmap", expanded=False):
        st.caption("Planned category engines are roadmap information, not active decision controls.")
        for item in FUTURE_CATEGORIES:
            st.write(f"Planned: {item}")


def render_sidebar():
    """Render a category-aware sidebar and return the backward-compatible assumptions contract."""
    apply_ui_theme()
    apply_c1_ux_overrides()
    st.sidebar.title("AI Procurement Copilot")
    st.sidebar.caption(EDITION)

    data_source, category, commodity, category_profile = _render_sourcing_setup()
    kraft_values = _render_kraft_inputs(category, commodity)
    laminate_values = _render_laminate_inputs(category, commodity)
    is_steel = category == "Raw Material Procurement" and commodity == "Steel"
    steel_values = render_steel_sidebar_controls({}) if is_steel else {}

    annual_volume, annual_volume_unit, fx_rate, display_currency = _render_commercial_basis(category_profile)
    generic_scenario_values = _render_generic_scenario_inputs(commodity, enabled=not is_steel)
    generic_allocation_values = _render_generic_allocation_rules(enabled=not is_steel)
    _render_about_roadmap()

    return build_sidebar_result(
        data_source=data_source,
        category=category,
        commodity=commodity,
        category_profile=category_profile,
        fx_rate=fx_rate,
        display_currency=display_currency,
        annual_volume=annual_volume,
        annual_volume_unit=annual_volume_unit,
        **generic_scenario_values,
        **generic_allocation_values,
        **kraft_values,
        **laminate_values,
        **steel_values,
    )
