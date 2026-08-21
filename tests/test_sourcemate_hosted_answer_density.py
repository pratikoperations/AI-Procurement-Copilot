from pathlib import Path

from modules.sourcemate_conversation_ui import _compact_answer_sections


def test_short_answer_remains_direct():
    answer = "Supplier A ranks first on the current governed score."
    summary, details = _compact_answer_sections(answer)
    assert summary == answer
    assert details is None


def test_long_answer_is_progressively_disclosed_without_losing_content():
    answer = (
        "The packaging TCO model starts from quoted unit price and adds governed cost exposures. "
        "Raw-material exposure is 60%, cost of capital is 12%, inventory carrying rate is 18%, "
        "maximum freight exposure is 6%, maximum failure probability is 20%, and the business-impact "
        "multiplier is 50%. The complete answer remains governed project evidence and must remain available."
    )
    summary, details = _compact_answer_sections(answer, max_summary_chars=180)
    assert len(summary) <= 180
    assert details is not None
    assert len(details) < len(answer)
    assert answer == f"{summary} {details}"


def test_long_answer_ui_uses_collapsed_detail_and_preserves_evidence():
    source = Path("modules/sourcemate_conversation_ui.py").read_text(encoding="utf-8")
    assert "def _compact_answer_sections(" in source
    assert 'if role == "assistant":' in source
    assert 'with st.expander("More detail", expanded=False):' in source
    assert "st.markdown(details)" in source
    assert 'st.caption("Evidence: "' in source
    assert 'st.markdown(str(message["content"]))' not in source


def test_answer_engine_and_governance_files_are_not_modified_by_presentation_fix():
    source = Path("modules/sourcemate_conversation_ui.py").read_text(encoding="utf-8")
    assert "answer_question(question_to_answer, current_context())" in source
    assert "external LLM" not in source
    assert "import openai" not in source.lower()
    assert "import requests" not in source.lower()
