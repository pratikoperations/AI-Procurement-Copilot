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


def test_global_bootstrap_mounts_after_page_config_and_wraps_scoring_read_only():
    source = Path("sitecustomize.py").read_text(encoding="utf-8")
    assert "set_page_config_with_sourcemate" in source
    assert "render_sourcemate_conversation(current_context(page), global_mount=True)" in source
    assert "result = original_enrich(suppliers_df, assumptions)" in source
    assert "publish_scored_context(result, assumptions)" in source
    assert "return result" in source


def test_all_streamlit_entry_points_use_page_config_for_global_bootstrap():
    entry_points = [
        Path("app.py"),
        Path("pages/8_Governed_Calculation_Explorer.py"),
        Path("pages/9_ERP_Upload_Preview.py"),
    ]
    for path in entry_points:
        assert path.exists(), path
        assert "st.set_page_config" in path.read_text(encoding="utf-8")


def test_widget_uses_shared_history_and_exactly_once_guard():
    source = Path("modules/sourcemate_conversation_ui.py").read_text(encoding="utf-8")
    assert '_SESSION_KEY = "sourcemate_conversation_history"' in source
    assert "reset_global_mount_guard" in source
    assert "if _RENDERED_THIS_RUN:" in source
    assert "publish_selected_presentation(presentation)" in source
    assert "overflow-x: auto" in source


def test_submit_renders_exchange_without_second_forced_rerun():
    source = Path("modules/sourcemate_conversation_ui.py").read_text(encoding="utf-8")
    submit_block = source.split("if not submitted:", 1)[1]
    assert "sourcemate_widget_submitted_exchange" in submit_block
    assert "for message in exchange:" in submit_block
    assert "st.rerun()" not in submit_block
