"""Bottom-right Streamlit widget for global project-wide SourceMate."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx

from modules.sourcemate_conversation import (
    SOURCEMATE_CONVERSATION_CONTRACT,
    answer_question,
)
from modules.sourcemate_global_context import current_context, publish_selected_presentation

_SESSION_KEY = "sourcemate_conversation_history"
_OPEN_KEY = "sourcemate_widget_open"
_MAX_MESSAGES = 16
_LAST_RENDER_TOKEN: int | None = None

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
    min-height: 3rem;
    border-radius: 999px;
    padding: 0.65rem 1rem;
    box-shadow: 0 8px 28px rgba(0, 0, 0, 0.28);
    font-weight: 700;
}
.st-key-sourcemate_widget_panel {
    position: fixed;
    right: 1rem;
    bottom: 5rem;
    z-index: 1000000;
    width: min(440px, calc(100vw - 1rem));
    max-width: min(440px, calc(100vw - 1rem));
    max-height: min(76vh, 720px);
    overflow-y: auto;
    overscroll-behavior: contain;
    padding: 1rem;
    border: 1px solid rgba(128, 128, 128, 0.45);
    border-radius: 1rem;
    background: var(--background-color, #0e1117);
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.38);
}
.st-key-sourcemate_widget_history {
    max-height: 42vh;
    overflow-y: auto;
    padding-right: 0.2rem;
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
        bottom: 8rem;
        width: calc(100vw - 1rem);
        max-width: calc(100vw - 1rem);
        max-height: 66vh;
        padding: 0.75rem;
    }
    .st-key-sourcemate_widget_history {
        max-height: 34vh;
    }
}
</style>
"""


def _current_render_token() -> int | None:
    """Return a token that changes with each Streamlit script run."""
    ctx = get_script_run_ctx(suppress_warning=True)
    return None if ctx is None else id(ctx)


def reset_global_mount_guard() -> None:
    """Allow the next render call while retaining duplicate protection within one run."""
    global _LAST_RENDER_TOKEN
    _LAST_RENDER_TOKEN = None


def _history() -> list[dict[str, Any]]:
    history = st.session_state.get(_SESSION_KEY)
    if not isinstance(history, list):
        history = []
        st.session_state[_SESSION_KEY] = history
    return history


def clear_sourcemate_history() -> None:
    """Clear only the current browser-session SourceMate history."""
    st.session_state[_SESSION_KEY] = []


def _toggle_panel() -> None:
    st.session_state[_OPEN_KEY] = not bool(st.session_state.get(_OPEN_KEY, False))


def _close_panel() -> None:
    st.session_state[_OPEN_KEY] = False


def _render_message(message: Mapping[str, Any]) -> None:
    with st.chat_message(str(message["role"])):
        st.markdown(str(message["content"]))
        refs = message.get("evidence_references") or []
        if refs:
            st.caption("Evidence references: " + " | ".join(str(item) for item in refs))
        if message.get("role") == "assistant":
            st.caption("Repository/live-context explanation. Human procurement review required.")


def _render_history(history: list[dict[str, Any]]) -> None:
    with st.container(key="sourcemate_widget_history"):
        if not history:
            with st.chat_message("assistant"):
                st.write(
                    "Ask about live supplier results, RFQ quotations, TCO-adjusted rates, qualification, scores, ranks, "
                    "recommendations, allocation, calculations, terms, abbreviations, evidence or governance."
                )
        for message in history:
            _render_message(message)


def render_sourcemate_conversation(
    presentation: Mapping[str, Any] | None = None,
    *,
    global_mount: bool = False,
) -> None:
    """Render one persistent SourceMate launcher and a rerun-safe fixed panel."""
    global _LAST_RENDER_TOKEN

    if presentation:
        publish_selected_presentation(presentation)

    render_token = _current_render_token()
    if render_token is not None and _LAST_RENDER_TOKEN == render_token:
        return
    _LAST_RENDER_TOKEN = render_token

    st.session_state.setdefault(_OPEN_KEY, False)
    context = current_context()
    st.markdown(_WIDGET_CSS, unsafe_allow_html=True)

    with st.container(key="sourcemate_widget_launcher"):
        launcher_label = "✕ Close SourceMate" if st.session_state[_OPEN_KEY] else "💬 SourceMate"
        st.button(
            launcher_label,
            key="sourcemate_launcher_toggle",
            on_click=_toggle_panel,
            width="stretch",
        )

    if not st.session_state[_OPEN_KEY]:
        return

    with st.container(key="sourcemate_widget_panel"):
        heading_columns = st.columns([5, 1])
        heading_columns[0].markdown("#### SourceMate — Project Assistant")
        heading_columns[1].button("✕", key="sourcemate_panel_close", on_click=_close_panel, width="stretch")
        st.caption(
            f"Contract {SOURCEMATE_CONVERSATION_CONTRACT}. Read-only, available across pages, and grounded in "
            "current live context or the governed project registry."
        )
        st.caption(f"Active page: {context.get('active_page', 'Unknown page')}")
        with st.expander("Evidence and authority boundaries", expanded=False):
            st.write(
                "No web browsing, external evidence retrieval, hidden recalculation, autonomous recommendation, supplier approval, "
                "award, production allocation or ERP writeback. Human procurement review remains mandatory."
            )

        history = _history()
        _render_history(history)

        with st.form("sourcemate_widget_form", clear_on_submit=True):
            question = st.text_input(
                "Ask SourceMate",
                placeholder="Ask about a supplier, RFQ quote, TCO, score, rank, formula or abbreviation",
                label_visibility="collapsed",
            )
            submitted = st.form_submit_button("Send", width="stretch")

        controls = st.columns(2)
        controls[0].button(
            "Clear conversation",
            key="sourcemate_clear",
            on_click=clear_sourcemate_history,
            width="stretch",
        )
        controls[1].caption("The panel stays open after Send. Use the launcher or ✕ to close it.")

        if not submitted:
            return
        if not str(question or "").strip():
            st.warning("Enter a project-related question.")
            return

        response = answer_question(question, current_context())
        exchange = [
            {"role": "user", "content": question},
            {
                "role": "assistant",
                "content": response["answer"],
                "evidence_references": response["evidence_references"],
                "intent": response["intent"],
                "human_review_required": response["human_review_required"],
            },
        ]
        history.extend(exchange)
        if len(history) > _MAX_MESSAGES:
            del history[:-_MAX_MESSAGES]
        st.session_state[_SESSION_KEY] = history
        st.session_state[_OPEN_KEY] = True

        with st.container(key="sourcemate_widget_submitted_exchange"):
            for message in exchange:
                _render_message(message)
