"""Focused assurance for Steel continuation into common intelligence navigation."""
from pathlib import Path


def test_steel_dashboard_returns_to_common_workflow() -> None:
    source = Path("modules/steel_ux.py").read_text(encoding="utf-8")
    function_source = source.split("def render_steel_governed_dashboard", 1)[1]

    assert "return to the common intelligence workflow" in function_source
    assert "st.stop()" not in function_source


def test_common_workflow_exposes_procurement_and_supplier_intelligence() -> None:
    source = Path("app.py").read_text(encoding="utf-8")

    assert '"4. Procurement Intelligence"' in source
    assert '"5. Supplier Intelligence"' in source
    assert "render_procurement_intelligence(" in source
    assert "render_supplier_intelligence(" in source
