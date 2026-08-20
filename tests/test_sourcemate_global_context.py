from pathlib import Path

from modules.sourcemate_conversation import answer_question, classify_intent
from modules.sourcemate_global_context import GLOSSARY, GLOBAL_CONTEXT_CONTRACT


def _context():
    return {
        "contract_version": GLOBAL_CONTEXT_CONTRACT,
        "active_page": "AI Procurement Copilot",
        "data_source": "Synthetic Demo",
        "synthetic_demo": True,
        "category": "Raw Material Procurement",
        "commodity": "Kraft Paper",
        "display_currency": "Both",
        "supplier_rows": [
            {
                "supplier": "Western Fibre Mills",
                "eligibility": "Eligible",
                "quote": 0.84,
                "quote_currency": "USD",
                "normalized_rate": 0.84,
                "tco_adjusted_rate": 0.91,
                "score": 82.4,
                "rank": 1,
                "risk": 76.0,
                "recommendation_status": "Recommended",
            },
            {
                "supplier": "National Kraft Industries",
                "eligibility": "Eligible",
                "quote": 0.96,
                "quote_currency": "USD",
                "normalized_rate": 0.96,
                "tco_adjusted_rate": 1.02,
                "score": 78.1,
                "rank": 2,
                "risk": 72.0,
                "recommendation_status": "Alternative",
            },
        ],
        "evidence_references": ["modules/scoring.py::enrich_supplier_scores", "app.py"],
        "calculation_overview": {},
        "assumptions": [],
        "calculation_trace": {"available": False},
        "reconciliation": {"available": False},
        "sourcemate": {"limitations": ["No web browsing.", "Human approval remains mandatory."]},
    }


def test_compound_vendor_quote_tco_score_rank_recommendation_answer():
    question = "Which Kraft Paper vendor qualified and what are quote, TCO adjusted rate, score, rank and recommendation?"
    response = answer_question(question, _context())
    assert response["intent"] == "live_supplier_results"
    assert "Western Fibre Mills" in response["answer"]
    assert "National Kraft Industries" in response["answer"]
    assert "RFQ quote" in response["answer"]
    assert "TCO-adjusted rate" in response["answer"]
    assert "Score" in response["answer"]
    assert "Rank" in response["answer"]
    assert "Recommendation" in response["answer"]
    assert "synthetic demonstration data" in response["answer"]
    assert response["calculation_executed"] is False
    assert response["action_executed"] is False


def test_named_supplier_question_filters_live_rows():
    response = answer_question("What did Western Fibre Mills quote?", _context())
    assert "Western Fibre Mills" in response["answer"]
    assert "National Kraft Industries" not in response["answer"]


def test_missing_live_fields_are_disclosed_not_inferred():
    context = _context()
    context["supplier_rows"][0]["tco_adjusted_rate"] = None
    response = answer_question("What is Western Fibre Mills TCO adjusted rate?", context)
    assert "Unavailable" in response["answer"]
    assert "rather than inferred" in response["answer"]


def test_live_supplier_intent_has_priority_for_compound_questions():
    assert classify_intent("Which vendor qualified and what is the TCO adjusted rate?", _context()) == "live_supplier_results"


def test_glossary_covers_required_abbreviations_and_terms():
    required = {
        "RFQ", "TCO", "SRM", "ESG", "OTIF", "EPR", "PCR", "FX", "MOQ",
        "DDP", "DAP", "CIF", "FOB", "EXW", "should-cost", "canonical currency",
        "reconciliation", "eligibility", "qualification", "recommendation", "allocation",
        "confidence", "provenance", "trace", "human review",
    }
    assert required.issubset(GLOSSARY)


def test_abbreviation_question_returns_direct_definition():
    response = answer_question("What does OTIF stand for?", _context())
    assert response["intent"] == "glossary"
    assert "On Time In Full" in response["answer"]


def test_external_forecast_still_fails_closed():
    response = answer_question("Predict Kraft Paper market prices next month", _context())
    assert response["intent"] == "unavailable"
    assert response["external_retrieval_used"] is False
    assert response["calculation_executed"] is False


def test_explicit_application_shell_replaces_implicit_widget_bootstrap_and_keeps_scoring_context_read_only():
    bootstrap_source = Path("sitecustomize.py").read_text(encoding="utf-8")
    shell_source = Path("modules/sourcemate_application_shell.py").read_text(encoding="utf-8")

    assert "set_page_config_with_sourcemate" not in bootstrap_source
    assert "render_sourcemate_conversation(current_context(page), global_mount=True)" not in bootstrap_source
    assert "def mount_global_sourcemate(" in shell_source
    assert "set_active_page(page_title)" in shell_source
    assert "publish_selected_presentation(presentation)" in shell_source
    assert "render_sourcemate_conversation(global_mount=True)" in shell_source

    assert "result = original_enrich(suppliers_df, assumptions)" in bootstrap_source
    assert "publish_scored_context(result, assumptions)" in bootstrap_source
    assert "return result" in bootstrap_source


def test_all_streamlit_entry_points_use_one_shared_sourcemate_shell_contract():
    app_source = Path("app.py").read_text(encoding="utf-8")
    sidebar_source = Path("modules/sidebar.py").read_text(encoding="utf-8")
    c1_source = Path("modules/c1_ux.py").read_text(encoding="utf-8")
    explorer_source = Path("pages/8_Governed_Calculation_Explorer.py").read_text(encoding="utf-8")
    erp_source = Path("pages/9_ERP_Upload_Preview.py").read_text(encoding="utf-8")

    assert "assumptions = render_sidebar()" in app_source
    assert "apply_c1_ux_overrides()" in sidebar_source
    assert 'mount_global_sourcemate("AI Procurement Copilot")' in c1_source

    assert 'mount_global_sourcemate("Governed Calculation Explorer")' in explorer_source
    assert 'mount_global_sourcemate("Governed Calculation Explorer", presentation=presentation)' in explorer_source
    assert "render_sourcemate_conversation(presentation)" not in explorer_source

    assert 'mount_global_sourcemate("ERP Upload Preview")' in erp_source
    assert erp_source.index('mount_global_sourcemate("ERP Upload Preview")') < erp_source.index("if uploaded_file is None:")


def test_widget_uses_shared_history_rerun_token_and_persistent_panel():
    source = Path("modules/sourcemate_conversation_ui.py").read_text(encoding="utf-8")
    assert '_SESSION_KEY = "sourcemate_conversation_history"' in source
    assert '_OPEN_KEY = "sourcemate_widget_open"' in source
    assert '_PENDING_QUESTION_KEY = "sourcemate_pending_question"' in source
    assert "get_script_run_ctx" in source
    assert "_current_render_token" in source
    assert "_LAST_RENDER_TOKEN == render_token" in source
    assert "publish_selected_presentation(presentation)" in source
    assert "sourcemate_widget_launcher" in source
    assert "sourcemate_widget_panel" in source
    assert "position: fixed" in source
    assert "overflow-x: auto" in source
    assert "st.popover(" not in source


def test_submit_refreshes_history_and_keeps_panel_open():
    source = Path("modules/sourcemate_conversation_ui.py").read_text(encoding="utf-8")
    assert "question_to_answer =" in source
    assert "history.extend(" in source
    assert "st.session_state[_OPEN_KEY] = True" in source
    assert "st.rerun()" in source
    assert "sourcemate_widget_submitted_exchange" not in source


def test_launcher_and_panel_controls_use_session_state_callbacks():
    source = Path("modules/sourcemate_conversation_ui.py").read_text(encoding="utf-8")
    assert "def _open_panel()" in source
    assert "def _close_panel()" in source
    assert "def _queue_question(question: str)" in source
    assert 'key="sourcemate_launcher_toggle"' in source
    assert 'key="sourcemate_panel_close"' in source
    assert "on_click=_open_panel" in source
    assert "on_click=_close_panel" in source
    assert "on_click=_queue_question" in source
    assert "✕ Close SourceMate" not in source
    assert "The panel stays open after Send" not in source
