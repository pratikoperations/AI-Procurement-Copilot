"""Prevent developer-style payload rendering in the Streamlit UI."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UI_FILES = [
    ROOT / "app.py",
    ROOT / "modules" / "supplier_intelligence_ui.py",
    ROOT / "modules" / "procurement_intelligence_ui.py",
    ROOT / "modules" / "dashboard.py",
]


def test_no_streamlit_json_renderer_in_ui_files():
    for path in UI_FILES:
        source = path.read_text(encoding="utf-8")
        assert "st.json(" not in source, f"Raw structured output renderer found in {path.name}"


def test_no_visible_json_download_labels():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert "Download Decision JSON" not in source
    assert "Download Supplier 360 JSON" not in source


def test_supplier_intelligence_has_readable_sections():
    source = (ROOT / "modules" / "supplier_intelligence_ui.py").read_text(encoding="utf-8")
    required = [
        "Executive overview",
        "Supplier 360 profile",
        "Performance dimension scores",
        "Mandatory financial disclaimer",
        "ESG dimension scores",
        "Innovation capability scores",
        "Governance matrix",
    ]
    for label in required:
        assert label in source


def test_machine_readable_payloads_are_download_only():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert "Decision Machine-Readable Audit Data" in source
    assert "Supplier 360 Machine-Readable Audit Data" in source


def test_dashboard_uses_executive_chart_labels():
    source = (ROOT / "modules" / "dashboard.py").read_text(encoding="utf-8")
    required = [
        "Risk Resilience Score",
        "Performance",
        "ESG Maturity",
        "Overall Decision Score",
        "Risk-Adjusted TCO",
        "Decision Dimension",
    ]
    for label in required:
        assert label in source
    assert 'y=["risk_score", "performance_score", "esg_score", "total_score"]' not in source


def test_raw_material_should_cost_heading_is_category_aware():
    source = (ROOT / "modules" / "dashboard.py").read_text(encoding="utf-8")
    assert "Raw Material Should-Cost Model" in source
    assert "Packaging Should-Cost Model" in source


def test_recommendation_explanations_use_business_language():
    source = (ROOT / "modules" / "supplier_recommendation_engine.py").read_text(encoding="utf-8")
    assert "Selected using deterministic comparison" not in source
    assert "Highest overall value after balancing cost, performance, governance, and business risk." in source
    assert "Lowest normalized commercial price before risk and total-cost adjustments." in source
