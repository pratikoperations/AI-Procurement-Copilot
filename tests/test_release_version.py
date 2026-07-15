from pathlib import Path

from streamlit.testing.v1 import AppTest

from modules.config import BUILD, EDITION, STATUS


def test_release_metadata_is_v1_0_1():
    assert EDITION == "Portfolio Edition v1.0.1"
    assert BUILD == "Version 1.0.1 - Stable Maintenance Release"
    assert STATUS == "Stable"


def test_app_docstring_and_display_use_v1_0_1():
    source = Path("app.py").read_text(encoding="utf-8")
    assert source.startswith('"""AI Procurement Copilot — Portfolio Edition v1.0.1."""')

    app = AppTest.from_file("app.py", default_timeout=30).run()
    assert not app.exception
    assert "Portfolio Edition v1.0.1" in [item.value for item in app.subheader]
    assert any(
        "Version 1.0.1 - Stable Maintenance Release" in item.value
        for item in app.success
    )
