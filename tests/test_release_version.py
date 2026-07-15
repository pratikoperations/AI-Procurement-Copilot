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


def test_primary_user_facing_release_documents_are_v1_0_1():
    readme = Path("README.md").read_text(encoding="utf-8")
    manifest = Path("VERSION_MANIFEST.md").read_text(encoding="utf-8")

    assert "**Release:** Portfolio Edition v1.0.1" in readme
    assert "Portfolio Edition v1.0.1 is the stable maintenance release" in readme
    assert "Portfolio Edition v1.0.1" in manifest
    assert "v1.0.1 is frozen as the stable maintenance release" in manifest
