"""Explicit application-shell mount for project-wide SourceMate.

Every Streamlit entry point calls this shared presentation helper. The helper only
publishes page/presentation context and renders the existing read-only SourceMate
widget; it does not calculate, score, rank, recommend, allocate, approve or mutate
procurement data.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from modules.sourcemate_conversation_ui import render_sourcemate_conversation
from modules.sourcemate_global_context import publish_selected_presentation, set_active_page


def mount_global_sourcemate(
    page_title: str,
    *,
    presentation: Mapping[str, Any] | None = None,
) -> None:
    """Mount exactly one SourceMate launcher for the current Streamlit script run."""
    set_active_page(page_title)
    if presentation:
        publish_selected_presentation(presentation)
    render_sourcemate_conversation(global_mount=True)
