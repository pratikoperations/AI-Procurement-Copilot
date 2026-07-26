from pathlib import Path

from streamlit.testing.v1 import AppTest

from modules.config import BUILD, EDITION, STATUS


def test_release_metadata_is_v1_2_portfolio_presentation():
    assert EDITION == "Portfolio Presentation Release v1.2"
    assert BUILD == "Version 1.2 - Portfolio Presentation Release"
    assert STATUS == "Portfolio Demonstration"


def test_app_docstring_and_display_use_v1_2():
    source = Path("app.py").read_text(encoding="utf-8")
    assert source.startswith('"""AI Procurement Copilot — Portfolio Presentation Release v1.2."""')

    app = AppTest.from_file("app.py", default_timeout=30).run()
    assert not app.exception
    assert app.title[0].value == "AI Procurement Copilot v1.2"
    assert any(
        "Governed, category-aware procurement decision support" in item.value
        for item in app.subheader
    )
    assert any(
        "Version 1.2 - Portfolio Presentation Release" in item.value
        for item in app.caption
    )
