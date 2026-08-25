"""Install one bounded presentation-only UX maturity layer.

The wrappers below only add semantic section surfaces around existing renderers.
Business services and SourceMate behavior remain authoritative and unchanged.
"""
from __future__ import annotations

from functools import wraps
from types import ModuleType
from typing import Any

from modules.ux_maturity_ui import semantic_section


def _wrap_renderer(
    module: ModuleType,
    name: str,
    *,
    family: str,
    phase: str,
    purpose: str,
) -> None:
    renderer = getattr(module, name)
    if getattr(renderer, "_aipc_ux_maturity", False):
        return

    @wraps(renderer)
    def wrapped(*args: Any, **kwargs: Any):
        with semantic_section(family, phase, purpose):
            return renderer(*args, **kwargs)

    wrapped._aipc_ux_maturity = True
    setattr(module, name, wrapped)


def install_ux_maturity_layer() -> None:
    """Wrap major existing workflow surfaces without changing their outputs."""
    try:
        from modules import dashboard

        for name, family, phase, purpose in (
            (
                "render_supplier_snapshot",
                "supplier",
                "ANALYSIS",
                "Compare supplier quotations, risk-adjusted TCO and governed decision dimensions.",
            ),
            (
                "render_should_cost_section",
                "cost",
                "ANALYSIS",
                "Review the existing governed should-cost target and component build-up.",
            ),
            (
                "render_tco_breakdown",
                "cost",
                "ANALYSIS",
                "Inspect the existing total-cost components behind supplier comparison.",
            ),
            (
                "render_executive_value",
                "output",
                "RECOMMENDATION / DECISION OUTPUT",
                "Surface the existing governed value metrics used for human procurement review.",
            ),
            (
                "render_allocation",
                "allocation",
                "RECOMMENDATION / DECISION OUTPUT",
                "Review the existing governed supplier-allocation result without creating an award.",
            ),
            (
                "render_scenario_table",
                "allocation",
                "ANALYSIS",
                "Stress-test the existing sourcing result across governed scenario outputs.",
            ),
            (
                "render_negotiation",
                "negotiation",
                "RECOMMENDATION / DECISION OUTPUT",
                "Review the existing negotiation position and savings simulation for human use.",
            ),
        ):
            _wrap_renderer(
                dashboard,
                name,
                family=family,
                phase=phase,
                purpose=purpose,
            )
    except Exception:
        pass

    try:
        from modules import procurement_intelligence_ui

        _wrap_renderer(
            procurement_intelligence_ui,
            "render_procurement_intelligence",
            family="supplier",
            phase="ANALYSIS",
            purpose="Review existing strategy, risk, scenario and sourcing intelligence in one governed workspace.",
        )
    except Exception:
        pass

    try:
        from modules import supplier_intelligence_currency_ui

        _wrap_renderer(
            supplier_intelligence_currency_ui,
            "render_supplier_intelligence",
            family="supplier",
            phase="ANALYSIS",
            purpose="Review existing Supplier 360, performance, risk, ESG and SRM evidence without changing supplier status.",
        )
    except Exception:
        pass
