"""Sidebar controls for the Streamlit app."""

import streamlit as st

from modules.c1_ux import apply_c1_ux_overrides
from modules.category_engine import ensure_category_profile, get_category_profile
from modules.config import DEFAULT_FX_RATE, EDITION, FUTURE_CATEGORIES, SUPPORTED_CATEGORIES
from modules.rfq_integration_controller import governed_route_enabled
from modules.ui_theme import apply_ui_theme
from modules.unit_display import annual_volume_label, canonical_unit, quantity_basis_caption

FX_RATE_MIN = 60
FX_RATE_MAX = 150
FX_RATE_STEP = 1


def build_sidebar_result(**values):
    """Build the governed sidebar return contract with a guaranteed category profile."""
    result = dict(values)
    result["category_profile"] = ensure_category_profile(result.get("category_profile"))
    result.setdefault("annual_volume_unit", canonical_unit(result["category_profile"].get("unit", "unit")))
    return result


def render_sidebar():
    """Render sidebar controls and always return a complete assumptions dictionary."""
    apply_ui_theme()
    apply_c1_ux_overrides()
    st.sidebar.title("AI Procurement Copilot")
    st.sidebar.caption(EDITION)

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
        st.sidebar.warning("Raw-material architecture is available as a foundation preview. Full category-specific scoring is planned for Build 0.9.4.")

    kraft_variant, kraft_gsm, kraft_strength_grade = "Recycled Kraft", 150, "22 BF"
    if category == "Raw Material Procurement" and commodity == "Kraft Paper":
        with st.sidebar.expander("Kraft Paper Assumptions", expanded=True):
            st.caption("Controlled synthetic profiles for portfolio demonstration; not live market specifications.")
            kraft_variant = st.selectbox("Fibre Basis", ["Recycled Kraft", "Virgin Kraft"], index=0)
            kraft_gsm = st.selectbox("GSM", [120, 150, 180], index=1)
            kraft_strength_grade = st.selectbox("Strength Grade", ["18 BF", "22 BF", "28 BF"], index=1)
            st.caption("Downstream linkage: Corrugated Board should-cost assumption review.")

    laminate_structure = "PET / PE"
    laminate_total_micron = 70
    laminate_print_profile = "Up to 4 colours"
    laminate_print_process = "Rotogravure"
    laminate_number_of_colours = 4
    laminate_adhesive_type = "Solvent-free"
    laminate_printing_loss_pct = 3.0
    laminate_lamination_loss_pct = 2.0
    laminate_slitting_loss_pct = 1.0
    laminate_tooling_status = "New"
    laminate_existing_tooling_available = "Not applicable"
    laminate_tooling_cost_per_colour_usd = 250.0
    laminate_tooling_lifetime_volume_kg = 250000.0
    if category == "Packaging Procurement" and commodity == "Flexible Laminates":
        with st.sidebar.expander("Flexible Laminate Assumptions", expanded=True):
            st.caption("Controlled synthetic C2 profiles; total micron is metadata only and does not infer physical mass or an approved technical specification.")
            laminate_structure = st.selectbox("Laminate Structure", ["PET / PE", "PET / MetPET / PE", "BOPP / CPP"], index=0)
            laminate_total_micron = st.number_input("Total Micron (metadata only)", min_value=35, max_value=140, value=70, step=1)
            laminate_print_profile = st.selectbox("Print Profile", ["Unprinted", "Up to 4 colours", "5–8 colours"], index=1)
            laminate_print_process = st.selectbox("Print Process", ["Rotogravure", "Flexographic"], index=0)
            laminate_number_of_colours = st.number_input("Number of Colours", min_value=0, max_value=8, value=4, step=1)
            laminate_adhesive_type = st.selectbox("Adhesive Type", ["Solvent-based", "Solvent-free"], index=1)
            laminate_printing_loss_pct = st.number_input("Printing Loss %", min_value=0.0, max_value=8.0, value=3.0, step=0.5)
            laminate_lamination_loss_pct = st.number_input("Lamination Loss %", min_value=0.0, max_value=6.0, value=2.0, step=0.5)
            laminate_slitting_loss_pct = st.number_input("Slitting Loss %", min_value=0.0, max_value=5.0, value=1.0, step=0.5)
            laminate_tooling_status = st.selectbox("Tooling Status", ["New", "Existing", "Not applicable"], index=0)
            laminate_existing_tooling_available = st.selectbox("Existing Tooling Available", ["Not applicable", "Yes", "No", "Not assessed"], index=0)
            laminate_tooling_cost_per_colour_usd = st.number_input("Tooling Cost per Colour USD", min_value=0.0, value=250.0, step=25.0)
            laminate_tooling_lifetime_volume_kg = st.number_input("Tooling Lifetime Volume kg", min_value=1.0, value=250000.0, step=10000.0)

    with st.sidebar.expander("Future Category Engines"):
        for item in FUTURE_CATEGORIES:
            st.write(f"Planned: {item}")

    st.sidebar.markdown("---")
    st.sidebar.subheader("Currency")
    fx_rate = st.sidebar.slider("USD-INR FX Rate", min_value=FX_RATE_MIN, max_value=FX_RATE_MAX, value=DEFAULT_FX_RATE, step=FX_RATE_STEP)
    display_currency = st.sidebar.radio("Display Currency", ["USD", "INR", "Both"], index=2)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Scenario Assumptions")
    annual_volume_unit = canonical_unit(category_profile.get("unit", "unit"))
    annual_volume = st.sidebar.number_input(annual_volume_label(annual_volume_unit), min_value=1000, value=500000, step=10000)
    st.sidebar.caption(quantity_basis_caption(annual_volume, annual_volume_unit))
    shock_label = "Paper / Raw Material Shock %" if commodity == "Kraft Paper" else "Raw Material Shock %"
    raw_material_shock = st.sidebar.slider(shock_label, -20, 40, 0) / 100
    freight_shock = st.sidebar.slider("Freight Shock %", -20, 80, 0) / 100
    demand_change = st.sidebar.slider("Demand Change %", -50, 50, 0) / 100

    st.sidebar.markdown("---")
    st.sidebar.subheader("Allocation Constraints")
    max_supplier_share = st.sidebar.slider("Max Supplier Share %", 50, 100, 75)
    min_backup_share = st.sidebar.slider("Minimum Backup Share %", 0, 40, 25)
    min_risk_score = st.sidebar.slider("Minimum Risk Score", 0, 100, 55)
    min_esg_score = st.sidebar.slider("Minimum ESG Score", 0, 100, 50)

    return build_sidebar_result(
        data_source=data_source, category=category, commodity=commodity, category_profile=category_profile,
        fx_rate=fx_rate, display_currency=display_currency, annual_volume=annual_volume,
        annual_volume_unit=annual_volume_unit, raw_material_shock=raw_material_shock,
        freight_shock=freight_shock, demand_change=demand_change, max_supplier_share=max_supplier_share,
        min_backup_share=min_backup_share, min_risk_score=min_risk_score, min_esg_score=min_esg_score,
        kraft_variant=kraft_variant, kraft_gsm=kraft_gsm, kraft_strength_grade=kraft_strength_grade,
        laminate_structure=laminate_structure, laminate_total_micron=laminate_total_micron,
        laminate_print_profile=laminate_print_profile, laminate_print_process=laminate_print_process,
        laminate_number_of_colours=laminate_number_of_colours, laminate_adhesive_type=laminate_adhesive_type,
        laminate_printing_loss_pct=laminate_printing_loss_pct,
        laminate_lamination_loss_pct=laminate_lamination_loss_pct,
        laminate_slitting_loss_pct=laminate_slitting_loss_pct,
        laminate_tooling_status=laminate_tooling_status,
        laminate_existing_tooling_available=laminate_existing_tooling_available,
        laminate_tooling_cost_per_colour_usd=laminate_tooling_cost_per_colour_usd,
        laminate_tooling_lifetime_volume_kg=laminate_tooling_lifetime_volume_kg,
    )
