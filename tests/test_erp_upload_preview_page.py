from pathlib import Path

PAGE_PATH = Path("pages/9_ERP_Upload_Preview.py")


def _page_source():
    return PAGE_PATH.read_text(encoding="utf-8")


def test_page_exists_and_uses_only_governed_erp_foundation_modules():
    source = _page_source()

    assert "modules.erp_workbook_loader" in source
    assert "modules.erp_structure_validator" in source
    assert "modules.erp_mapping_profiles" in source
    assert "modules.erp_upload_preview" in source

    prohibited_imports = (
        "modules.scoring",
        "modules.recommendation",
        "modules.allocation",
        "modules.allocation_optimizer",
        "modules.decision_engine",
        "modules.data_loader",
        "modules.supplier_comparison",
        "modules.exports",
    )
    assert all(name not in source for name in prohibited_imports)


def test_page_is_single_xlsx_read_only_preview():
    source = _page_source()

    assert 'type=["xlsx"]' in source
    assert "accept_multiple_files=False" in source
    assert "st.session_state" not in source
    assert "download_button" not in source
    assert "open(" not in source
    assert "write_bytes" not in source
    assert "write_text" not in source


def test_page_enforces_blocked_state_before_mapping_display():
    source = _page_source()

    blocked_position = source.index("if validation.status == BLOCKED:")
    stop_position = source.index("st.stop()", blocked_position)
    profile_position = source.index("selected_profile =", blocked_position)

    assert blocked_position < stop_position < profile_position
    assert "mapping preview is suppressed" in source


def test_governance_wording_is_present():
    source = _page_source().lower()

    required_phrases = (
        "read-only structural validation",
        "no procurement analysis",
        "draft static mapping",
        "not live integrations",
        "no data was saved",
        "human review remains mandatory",
    )
    assert all(phrase in source for phrase in required_phrases)


def test_page_does_not_offer_normalization_or_processing_actions():
    source = _page_source().lower()

    prohibited_actions = (
        "continue to analysis",
        "normalize workbook",
        "match supplier",
        "match material",
        "run procurement",
        "save workbook",
    )
    assert all(action not in source for action in prohibited_actions)
