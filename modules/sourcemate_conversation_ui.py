"""Bottom-right Streamlit widget for global project-wide SourceMate."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import streamlit as st

from modules.sourcemate_conversation import (
    SOURCEMATE_CONVERSATION_CONTRACT,
    answer_question,
)
from modules.sourcemate_global_context import current_context, publish_selected_presentation

_SESSION_KEY = "sourcemate_conversation_history"
_OPEN_KEY = "sourcemate_widget_open"
_MAX_MESSAGES = 16

_WIDGET_CSS = """
<style>
.st-key-sourcemate_widget_launcher {
    position: fixed;
    right: 1rem;
    bottom: 1rem;
    z-index: 1000001;
    width: auto;
    max-width: calc(100vw - 1rem);
}
.st-key-sourcemate_widget_launcher button {
    min-height: 2.75rem;
    border-radius: 999px;
    padding: 0.55rem 0.9rem;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.24);
    font-weight: 700;
}
.st-key-sourcemate_widget_panel {
    position: fixed;
    right: 1rem;
    bottom: 1rem;
    z-index: 1000000;
    width: min(420px, calc(100vw - 1rem));
    max-width: min(420px, calc(100vw - 1rem));
    max-height: min(54vh, 620px);
    overflow-y: auto;
    overscroll-behavior: contain;
    padding: 0.85rem;
    border: 1px solid rgba(128, 128, 128, 0.38);
    border-radius: 1rem;
    background: var(--background-color, #0e1117);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.34);
}
.st-key-sourcemate_widget_history {
    max-height: 34vh;
    overflow-y: auto;
    padding-right: 0.15rem;
}
.st-key-sourcemate_widget_history table {
    display: block;
    max-width: 100%;
    overflow-x: auto;
    white-space: nowrap;
}
@media (max-width: 640px) {
    .st-key-sourcemate_widget_launcher {
        right: 0.5rem;
        bottom: 4.25rem;
        max-width: calc(100vw - 1rem);
    }
    .st-key-sourcemate_widget_panel {
        right: 0.5rem;
        bottom: 4.25rem;
        width: calc(100vw - 1rem);
        max-width: calc(100vw - 1rem);
        max-height: 52vh;
        padding: 0.7rem;
    }
    .st-key-sourcemate_widget_history {
        max-height: 28vh;
    }
}
</style>
"""


def _history() -> list[dict[str, Any]]:
    history = st.session_state.get(_SESSION_KEY)
    if not isinstance(history, list):
        history = []
        st.session_state[_SESSION_KEY] = history
    return history


def clear_sourcemate_history() -> None:
    """Clear only the current browser-session SourceMate history."""
    st.session_state[_SESSION_KEY] = []


def _open_panel() -> None:
    st.session_state[_OPEN_KEY] = True


def _close_panel() -> None:
    st.session_state[_OPEN_KEY] = False


def _render_message(message: Mapping[str, Any]) -> None:
    with st.chat_message(str(message["role"])):
        st.markdown(str(message["content"]))
        refs = message.get("evidence_references") or []
        if refs:
            st.caption("Evidence: " + " | ".join(str(item) for item in refs))


def _render_history(history: list[dict[str, Any]]) -> None:
    for message in history:
        _render_message(message)


def render_sourcemate_conversation(
    presentation: Mapping[str, Any] | None = None,
    *,
    global_mount: bool = False,
) -> None:
    """Render one persistent SourceMate launcher and fixed conversation panel."""
    del global_mount  # explicit application-shell mounting guarantees one call per entry point

    if presentation:
        publish_selected_presentation(presentation)

    st.session_state.setdefault(_OPEN_KEY, False)
    context = current_context()
    active_page = str(context.get("active_page", "Current page"))
    st.markdown(_WIDGET_CSS, unsafe_allow_html=True)

    if not st.session_state[_OPEN_KEY]:
        with st.container(key="sourcemate_widget_launcher"):
            st.button(
                "💬 SourceMate",
                key="sourcemate_launcher_toggle",
                on_click=_open_panel,
                width="stretch",
            )
        return

    with st.container(key="sourcemate_widget_panel"):
        heading_columns = st.columns([6, 1])
        heading_columns[0].markdown("#### SourceMate")
        heading_columns[1].button("✕", key="sourcemate_panel_close", on_click=_close_panel, width="stretch")
        st.caption(f"{active_page} · Read-only · Human review required")

        history = _history()
        history_container = st.container(key="sourcemate_widget_history")

        with st.form("sourcemate_widget_form", clear_on_submit=True):
            question = st.text_input(
                "Ask SourceMate",
                placeholder="Ask SourceMate…",
                label_visibility="collapsed",
            )
            submitted = st.form_submit_button("Send", width="stretch")

        with st.expander("ⓘ Details & controls", expanded=False):
            st.caption(
                "Read-only. No web browsing, external evidence retrieval, hidden recalculation, autonomous supplier approval, "
                "award, production allocation or ERP writeback. Human procurement review remains mandatory."
            )
            st.caption(f"Contract: {SOURCEMATE_CONVERSATION_CONTRACT}")
            st.button(
                "Clear conversation",
                key="sourcemate_clear",
                on_click=clear_sourcemate_history,
                width="stretch",
            )

        if submitted:
            question_to_answer = str(question or "").strip()
            if not question_to_answer:
                st.warning("Enter a project-related question.")
            else:
                response = answer_question(question_to_answer, current_context())
                history.extend(
                    [
                        {"role": "user", "content": question_to_answer},
                        {
                            "role": "assistant",
                            "content": response["answer"],
                            "evidence_references": response["evidence_references"],
                            "intent": response["intent"],
                            "human_review_required": response["human_review_required"],
                        },
                    ]
                )
                if len(history) > _MAX_MESSAGES:
                    del history[:-_MAX_MESSAGES]
                st.session_state[_SESSION_KEY] = history
                st.session_state[_OPEN_KEY] = True

        with history_container:
            _render_history(history)
