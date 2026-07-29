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


def test_session_reset_contract_includes_digest_and_contract_version():
    assert "governed_v13_handoff_digest" in SESSION_REVIEW_KEYS
    assert "governed_v13_handoff_manifest_digest" in SESSION_REVIEW_KEYS
    assert "governed_v13_handoff_contract_version" in SESSION_REVIEW_KEYS
