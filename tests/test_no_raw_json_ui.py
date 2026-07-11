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
    assert "Machine-Readable Decision Audit Data" in source
    assert "Supplier 360 Audit Data" in source
