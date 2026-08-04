"""Global presentation bootstrap for Streamlit entry points.

The bootstrap wraps presentation hooks only. Existing business functions remain
authoritative and their return values are passed through unchanged.
"""
from __future__ import annotations


_LEGACY_PUBLIC_INTENTS = (
    "calculation",
    "assumptions",
    "trace",
    "reconciliation",
    "evidence",
    "project_knowledge",
    "limitations",
    "clarification",
    "unavailable",
)


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
                from modules.sourcemate_conversation_ui import (
                    render_sourcemate_conversation,
                    reset_global_mount_guard,
                )

                reset_global_mount_guard()
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

    try:
        from modules import dashboard
        from modules.decision_clarity_ui import render_decision_clarity

        if not getattr(dashboard.render_executive_dashboard, "_aipc_decision_clarity", False):
            original_dashboard = dashboard.render_executive_dashboard

            def render_executive_dashboard_with_clarity(scored_df, assumptions, confidence=None):
                render_decision_clarity(scored_df, assumptions, confidence)
                with st.expander("Detailed executive dashboard", expanded=False):
                    return original_dashboard(scored_df, assumptions, confidence)

            render_executive_dashboard_with_clarity._aipc_decision_clarity = True
            dashboard.render_executive_dashboard = render_executive_dashboard_with_clarity
    except Exception:
        # The clarity layer is presentation-only and must never block the application.
        pass

    try:
        from modules.ux_acceptance_corrections import install_ux_acceptance_corrections

        install_ux_acceptance_corrections()
    except Exception:
        # Hosted acceptance formatting must never block authoritative application routes.
        pass

    try:
        # Preserve the established public intent catalogue for compatibility.
        # Live-supplier and glossary handling remain internal deterministic subroutes.
        from modules import sourcemate_conversation

        sourcemate_conversation.SUPPORTED_INTENTS = _LEGACY_PUBLIC_INTENTS
    except Exception:
        pass


_install()
