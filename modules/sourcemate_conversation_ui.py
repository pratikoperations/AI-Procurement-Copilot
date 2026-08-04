"""Streamlit UI for SourceMate Conversational Basic Interview Version."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import streamlit as st

from modules.sourcemate_conversation import (
    SOURCEMATE_CONVERSATION_CONTRACT,
    answer_question,
)

_SESSION_KEY = "sourcemate_conversation_history"
_MAX_MESSAGES = 12


def _history() -> list[dict[str, Any]]:
    history = st.session_state.get(_SESSION_KEY)
    if not isinstance(history, list):
        history = []
        st.session_state[_SESSION_KEY] = history
    return history


def clear_sourcemate_history() -> None:
    """Clear only the current browser-session SourceMate history."""
    st.session_state[_SESSION_KEY] = []


def render_sourcemate_conversation(presentation: Mapping[str, Any]) -> None:
    """Render a fixed, read-only chat panel grounded in current evidence."""
    st.markdown("---")
    st.subheader("SourceMate — Conversational Basic")
    st.caption(
        f"Contract {SOURCEMATE_CONVERSATION_CONTRACT}. Read-only, current-session conversation grounded only in the selected calculation evidence."
    )
    st.info(
        "SourceMate does not browse the web, retrieve external evidence, execute formulas, recommend autonomous awards, "
        "allocate production, approve suppliers, or write to ERP. Human procurement review remains mandatory."
    )

    controls = st.columns([1, 3])
    if controls[0].button("Clear conversation", use_container_width=True):
        clear_sourcemate_history()
        st.rerun()
    controls[1].caption("Suggested: What is the result? What assumptions were used? Is the evidence reconciled? What are the limitations?")

    history = _history()
    if not history:
        with st.chat_message("assistant"):
            st.write(
                "Ask about the selected calculation, assumptions, trace, reconciliation, evidence coverage, or limitations. "
                "Unsupported questions will return a controlled not-available response."
            )

    for message in history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            refs = message.get("evidence_references") or []
            if refs:
                st.caption("Evidence references: " + " | ".join(refs))
            if message.get("role") == "assistant":
                st.caption("Generated explanation from current governed evidence. Human review required.")

    question = st.chat_input("Ask SourceMate about the selected governed calculation")
    if not question:
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
