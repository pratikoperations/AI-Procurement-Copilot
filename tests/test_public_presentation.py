from pathlib import Path

from streamlit.testing.v1 import AppTest

APP_PATH = Path("app.py")


def _source():
    return APP_PATH.read_text(encoding="utf-8")


def test_public_application_removes_interview_guide():
    source = _source()

    assert "Interview Guide" not in source
    assert "Interview Talking Points" not in source
    assert "generate_interview_talking_points" not in source


def test_public_application_uses_mobile_safe_native_navigation():
    source = _source()

    assert "st.tabs(" not in source
    assert 'st.selectbox(\n    "Explore the sourcing workflow"' in source
    assert "Choose one section at a time" in source


def test_navigation_contract_contains_seven_numbered_sections():
    source = _source()
    expected = (
        "1. Decision Summary",
        "2. Cost and Risk",
        "3. Scenarios and Negotiation",
        "4. Procurement Intelligence",
        "5. Supplier Intelligence",
        "6. Executive Outputs",
        "7. Downloads",
    )

    assert all(label in source for label in expected)
    assert "8. Interview Guide" not in source


def test_executive_first_claim_safe_messages_are_compact_and_present():
    source = _source().lower()

    required = (
        "portfolio demo",
        "read-only",
        "validation-gated",
        "no live erp integration",
        "synthetic/demo evidence where indicated",
        "human procurement approval remains mandatory",
    )
    assert all(message in source for message in required)
    assert 'status_columns[0].info("portfolio demonstration")' not in source
    assert 'status_columns[1].info("read-only operation")' not in source
    assert 'status_columns[2].info("validation-gated")' not in source
    assert 'status_columns[3].info("no live erp integration")' not in source


def test_non_blocking_allocation_governance_is_collapsed_not_banner_stacked():
    source = _source()

    assert 'with st.expander("Governance & Evidence Details", expanded=False):' in source
    assert "governance_notes = list(dict.fromkeys(allocation_route_result.warnings))" in source
    assert "for warning in allocation_route_result.warnings:\n        st.warning(warning)" not in source
    assert 'st.warning("Partial evidence captured before adapter failure")' not in source
    assert 'st.error(f"Canonical allocation route is blocked: {route_status}")' in source


def test_downloads_remain_available_and_grouped():
    source = _source()

    assert source.count("download_button(") == 9
    assert "Business-facing outputs" in source
    assert "Machine-readable audit outputs" in source
    assert "use_container_width=True" in source


def test_public_application_smoke_and_default_navigation():
    app = AppTest.from_file(str(APP_PATH), default_timeout=30).run()

    assert not app.exception
    assert app.title[0].value == "AI Procurement Copilot v1.2"
    workflow_selectors = [
        item for item in app.selectbox
        if item.label == "Explore the sourcing workflow"
    ]
    assert len(workflow_selectors) == 1
    assert workflow_selectors[0].value == "1. Decision Summary"
