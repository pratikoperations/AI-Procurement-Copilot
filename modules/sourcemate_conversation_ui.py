"""Bottom-right Streamlit widget for project-wide SourceMate."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import streamlit as st

from modules.sourcemate_conversation import (
    SOURCEMATE_CONVERSATION_CONTRACT,
    answer_question,
)

_SESSION_KEY = "sourcemate_conversation_history"
_MAX_MESSAGES = 16

_WIDGET_CSS = """
<style>
.st-key-sourcemate_widget_shell {
    position: fixed;
    right: 1rem;
    bottom: 1rem;
    z-index: 1000000;
    width: auto;
    max-width: calc(100vw - 1rem);
}
.st-key-sourcemate_widget_shell [data-testid="stPopover"] > button {
    min-height: 3rem;
    border-radius: 999px;
    padding: 0.65rem 1rem;
    box-shadow: 0 8px 28px rgba(0, 0, 0, 0.28);
    font-weight: 700;
}
div[data-testid="stPopoverBody"] {
    width: min(420px, calc(100vw - 1rem));
    max-width: min(420px, calc(100vw - 1rem));
    max-height: min(72vh, 680px);
    overflow-y: auto;
    overscroll-behavior: contain;
}
.st-key-sourcemate_widget_history {
    max-height: 42vh;
    overflow-y: auto;
    padding-right: 0.2rem;
}
@media (max-width: 640px) {
    .st-key-sourcemate_widget_shell {
        right: 0.5rem;
        bottom: 4.25rem;
        max-width: calc(100vw - 1rem);
    }
    div[data-testid="stPopoverBody"] {
        width: calc(100vw - 1rem);
        max-width: calc(100vw - 1rem);
        max-height: 68vh;
    }
    .st-key-sourcemate_widget_history {
        max-height: 34vh;
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


def _render_history(history: list[dict[str, Any]]) -> None:
    with st.container(key="sourcemate_widget_history"):
        if not history:
            with st.chat_message("assistant"):
                st.write(
                    "Ask about this project: calculations, TCO, risk, scoring, SRM, supplier intelligence, allocation, "
                    "scenarios, RFQ, currency, evidence, governance or limitations."
                )
        for message in history:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                refs = message.get("evidence_references") or []
                if refs:
                    st.caption("Evidence references: " + " | ".join(refs))
                if message.get("role") == "assistant":
                    st.caption("Repository-grounded explanation. Human procurement review required.")


def render_sourcemate_conversation(presentation: Mapping[str, Any]) -> None:
    """Render a persistent bottom-right SourceMate launcher and popover panel."""
    st.markdown(_WIDGET_CSS, unsafe_allow_html=True)
    with st.container(key="sourcemate_widget_shell"):
        with st.popover("💬 SourceMate"):
            st.markdown("#### SourceMate — Project Assistant")
            st.caption(
                f"Contract {SOURCEMATE_CONVERSATION_CONTRACT}. Read-only and grounded in selected live evidence or the governed project registry."
            )
            with st.expander("Evidence and authority boundaries", expanded=False):
                st.write(
                    "No web browsing, external evidence retrieval, formula execution, autonomous recommendation, supplier approval, "
                    "award, production allocation or ERP writeback. Human procurement review remains mandatory."
                )

            history = _history()
            _render_history(history)

            with st.form("sourcemate_widget_form", clear_on_submit=True):
                question = st.text_input(
                    "Ask SourceMate",
                    placeholder="Ask about TCO, SRM, scoring, allocation, RFQ or the selected calculation",
                    label_visibility="collapsed",
                )
                submitted = st.form_submit_button("Send", use_container_width=True)

            controls = st.columns(2)
            if controls[0].button("Clear conversation", key="sourcemate_clear", use_container_width=True):
                clear_sourcemate_history()
                st.rerun()
            controls[1].caption("Close or minimize by tapping the SourceMate launcher or outside the panel.")

            if not submitted:
                return
            if not str(question or "").strip():
                st.warning("Enter a project-related question.")
                return

            response = answer_question(question, presentation)
            history.extend(
                [
                    {"role": "user", "content": question},
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
            st.rerun()
