from pathlib import Path

from modules.sourcemate_conversation_ui import _compact_answer_sections


def test_short_answer_remains_direct():
    answer = "Supplier A ranks first on the current governed score."
    summary, details = _compact_answer_sections(answer)
    assert summary == answer
    assert details is None


def test_long_answer_is_concise_while_full_governed_content_remains_available():
    answer = (
        "The packaging TCO model starts from quoted unit price and adds governed cost exposures. "
        "Raw-material exposure is 60%, cost of capital is 12%, inventory carrying rate is 18%, "
        "maximum freight exposure is 6%, maximum failure probability is 20%, and the business-impact "
        "multiplier is 50%. The complete answer remains governed project evidence and must remain available."
    )
    summary, details = _compact_answer_sections(answer, max_summary_chars=180)
    assert len(summary) <= 181  # optional ellipsis may add one display character
    assert summary != answer
    assert details == answer


def test_long_unpunctuated_answer_uses_bounded_summary_without_losing_full_detail():
    answer = " ".join(["governed-evidence"] * 80)
    summary, details = _compact_answer_sections(answer, max_summary_chars=120)
    assert summary.endswith("…")
    assert len(summary) <= 121
    assert details == answer


def test_long_answer_ui_uses_collapsed_detail_and_preserves_evidence():
    source = Path("modules/sourcemate_conversation_ui.py").read_text(encoding="utf-8")
    assert "def _compact_answer_sections(" in source
    assert 'if role == "assistant":' in source
    assert 'with st.expander("More detail", expanded=False):' in source
    assert "st.markdown(details)" in source
    assert 'st.caption("Evidence: "' in source
    assert 'st.markdown(str(message["content"]))' not in source


def test_post_submit_contract_has_no_forced_rerun_or_duplicate_render_guard():
    source = Path("modules/sourcemate_conversation_ui.py").read_text(encoding="utf-8")
    assert "def _append_exchange(" in source
    assert "st.session_state[_OPEN_KEY] = True" in source
    assert "st.rerun()" not in source
    assert "get_script_run_ctx" not in source
    assert "_LAST_RENDER_TOKEN" not in source
    assert "history_container = st.container" in source
    assert "with history_container:" in source


def test_answer_engine_and_governance_files_are_not_modified_by_presentation_fix():
    source = Path("modules/sourcemate_conversation_ui.py").read_text(encoding="utf-8")
    assert "answer_question(question, current_context())" in source
    assert "external LLM" not in source
    assert "import openai" not in source.lower()
    assert "import requests" not in source.lower()
