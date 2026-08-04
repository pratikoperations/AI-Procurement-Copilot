"""Global SourceMate bootstrap for Streamlit entry points.

The bootstrap wraps presentation hooks only. Existing business functions remain
authoritative and their return values are passed through unchanged.
"""
from __future__ import annotations


def _install() -> None:
    try:
        import streamlit as st
    except Exception:
        return

    if not getattr(st.set_page_config, "_aipc_global_sourcemate", False):
        original_set_page_config = st.set_page_config

        def set_page_config_with_sourcemate(*args, **kwargs):
            result = original_set_page_config(*args, **kwargs)
            try:
                from modules.sourcemate_global_context import current_context
                from modules.sourcemate_conversation_ui import render_sourcemate_conversation

                page = str(kwargs.get("page_title") or "AI Procurement Copilot")
                render_sourcemate_conversation(current_context(page), global_mount=True)
            except Exception:
                # A presentation helper must never prevent the governed page from loading.
                pass
            return result

        set_page_config_with_sourcemate._aipc_global_sourcemate = True
        st.set_page_config = set_page_config_with_sourcemate

    try:
        from modules import scoring
        from modules.sourcemate_global_context import publish_scored_context

        if not getattr(scoring.enrich_supplier_scores, "_aipc_global_sourcemate", False):
            original_enrich = scoring.enrich_supplier_scores

            def enrich_supplier_scores_with_context(suppliers_df, assumptions):
                result = original_enrich(suppliers_df, assumptions)
                try:
                    publish_scored_context(result, assumptions)
                except Exception:
                    pass
                return result

            enrich_supplier_scores_with_context._aipc_global_sourcemate = True
            scoring.enrich_supplier_scores = enrich_supplier_scores_with_context
    except Exception:
        pass


_install()
