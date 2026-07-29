from pathlib import Path

from modules.rfq_integration_controller import (
    HANDOFF_FLAG,
    SESSION_REVIEW_KEYS,
    analytical_handoff_enabled,
    reset_session_for_upload,
)


def test_handoff_feature_flag_is_default_off_and_fail_closed():
    assert analytical_handoff_enabled({}) == (False, None)
    assert analytical_handoff_enabled({HANDOFF_FLAG: "true"}) == (True, None)
    enabled, warning = analytical_handoff_enabled({HANDOFF_FLAG: "maybe"})
    assert not enabled
    assert HANDOFF_FLAG in warning


def test_upload_change_invalidates_all_handoff_identity_keys():
    state = {"governed_v13_active_upload_hash": "old"}
    for key in SESSION_REVIEW_KEYS:
        state[key] = "value"
    assert reset_session_for_upload(state, b"new workbook")
    assert all(key not in state for key in SESSION_REVIEW_KEYS)
    assert state["governed_v13_active_upload_hash"]


def test_session_reset_contract_includes_ranking_and_handoff_identity():
    required = {
        "governed_v13_ranking_confirmations",
        "governed_v13_handoff_digest",
        "governed_v13_handoff_manifest_digest",
        "governed_v13_handoff_contract_version",
    }
    assert required.issubset(SESSION_REVIEW_KEYS)


def test_application_reconstructs_and_passes_typed_ranking_confirmations():
    source = Path("app.py").read_text(encoding="utf-8")
    assert "RankingMappingConfirmation(**item)" in source
    assert "ranking_confirmations=ranking_confirmations" in source
    assert 'governed_v13_ranking_confirmations' in source
    assert "render_ranking_mapping_confirmations" in source


def test_ranking_confirmation_change_resets_selection_and_handoff_state():
    source = Path("app.py").read_text(encoding="utf-8")
    confirmation_assignment = source.index('st.session_state["governed_v13_ranking_confirmations"]')
    reset_block = source[confirmation_assignment:confirmation_assignment + 1000]
    for key in (
        "governed_v13_selected_event",
        "governed_v13_selected_rfq_number",
        "governed_v13_selected_rfq_item",
        "governed_v13_acknowledged_warnings",
        "governed_v13_handoff_digest",
    ):
        assert key in reset_block
