from pathlib import Path

from modules.sourcemate_conversation import (
    SOURCEMATE_CONVERSATION_CONTRACT,
    SUPPORTED_INTENTS,
    answer_question,
    classify_intent,
)
from modules.sourcemate_project_knowledge import (
    PROJECT_KNOWLEDGE,
    PROJECT_KNOWLEDGE_CONTRACT,
    project_topic_catalogue,
    search_project_knowledge,
)


def _presentation():
    return {
        "calculation_overview": {
            "calculation_id": "PET-001",
            "formula_id": "F-RM-SHOULDCOST",
            "business_name": "PET Resin Target Unit Cost",
            "source_module": "modules/raw_material_cost.py",
            "source_function": "calculate_raw_material_should_cost",
            "result": {"target_unit_cost_usd": 1.27, "commodity": "PET Resin"},
            "principal_result_key": "target_unit_cost_usd",
            "unit": "USD/kg",
        },
        "assumptions": [
            {
                "assumption_id": "A-1",
                "key": "annual_volume",
                "effective_value": 500000,
                "source_reference": "Controlled portfolio demonstration",
            }
        ],
        "calculation_trace": {
            "available": True,
            "trace_id": "trace-1",
            "contract_version": "AIPC-CALC-TRACE-1.0",
            "human_review": "required",
            "intermediate_steps": [{"name": "step"}],
            "unresolved_or_rejected_parameters": [],
        },
        "reconciliation": {
            "available": True,
            "reconciliation_id": "recon-1",
            "authoritative_service": "calculate_raw_material_should_cost:PET",
            "status": "exact_match",
            "exact_matches": ["$raw_output"],
            "tolerated_differences": [],
            "mismatches": [],
            "unavailable_evidence": [],
        },
        "sourcemate": {
            "contract_version": "AIPC-SOURCEMATE-BASIC-1.0",
            "calculation_id": "PET-001",
            "formula_id": "F-RM-SHOULDCOST",
            "coverage_id": "REC-PET",
            "coverage_classification": "adapter_backed",
            "export_evidence": [{"evidence_id": "E-1"}],
            "assumption_sources": [{"assumption_id": "A-1"}],
            "external_verification_claimed": False,
            "limitations": ["No web browsing.", "Human approval remains mandatory."],
        },
    }


def test_contracts_and_supported_intents_are_bounded():
    assert SOURCEMATE_CONVERSATION_CONTRACT == "AIPC-SOURCEMATE-PROJECT-WIDGET-BIV-1.0"
    assert PROJECT_KNOWLEDGE_CONTRACT == "AIPC-SOURCEMATE-PROJECT-KNOWLEDGE-1.0"
    assert SUPPORTED_INTENTS == (
        "live_supplier_results",
        "calculation",
        "assumptions",
        "trace",
        "reconciliation",
        "evidence",
        "glossary",
        "project_knowledge",
        "limitations",
        "clarification",
        "unavailable",
    )


def test_live_selected_evidence_keeps_precedence():
    assert classify_intent("What assumptions were used?") == "assumptions"
    assert classify_intent("Show the calculation trace") == "trace"
    assert classify_intent("Are there reconciliation mismatches?") == "reconciliation"
    assert classify_intent("What is the current calculation result?") == "calculation"

    presentation = _presentation()
    assert "annual_volume" in answer_question("What assumptions were used?", presentation)["answer"]
    assert "trace-1" in answer_question("Show the calculation trace", presentation)["answer"]
    assert "1 exact match" in answer_question("Are there reconciliation mismatches?", presentation)["answer"]
    assert "1.27" in answer_question("What is the current calculation result?", presentation)["answer"]


def test_tco_question_returns_registered_percentages_and_sources():
    response = answer_question("What percentage is considered in TCO for each parameter?", _presentation())
    assert response["intent"] == "project_knowledge"
    assert "raw-material exposure 60%" in response["answer"]
    assert "cost of capital 12%" in response["answer"]
    assert "inventory carrying rate 18%" in response["answer"]
    assert "maximum freight exposure 6%" in response["answer"]
    assert "business-impact multiplier 50%" in response["answer"]
    assert "modules/tco.py::calculate_supplier_tco" in response["evidence_references"]


def test_srm_question_returns_weights_thresholds_and_bifurcation():
    response = answer_question("Give SRM rating bifurcation", _presentation())
    assert response["intent"] == "project_knowledge"
    assert "| Particular | Weight |" in response["answer"]
    assert "| Supplier performance | 25% |" in response["answer"]
    assert "| Risk score | 20% |" in response["answer"]
    assert "| Innovation | 15% |" in response["answer"]
    assert "| Strategic | Strategic index at least 80" in response["answer"]
    assert "| Exit Candidate |" in response["answer"]
    assert "modules/srm_engine.py::classify_supplier_relationship" in response["evidence_references"]


def test_project_registry_covers_authorized_topic_catalogue():
    topics = project_topic_catalogue()
    assert len(PROJECT_KNOWLEDGE) >= 16
    expected = (
        "project architecture and scope",
        "category engines",
        "should-cost methodology",
        "total cost of ownership",
        "supplier risk",
        "supplier scoring and performance",
        "supplier relationship management classification",
        "financial ESG and innovation intelligence",
        "supplier recommendations",
        "multi-supplier allocation",
        "scenario analysis",
        "RFQ processing",
        "assumptions and precedence",
        "currency and unit governance",
        "exports evidence and reconciliation",
        "governance limitations and deferred capabilities",
    )
    for topic in expected:
        assert topic in topics


def test_retrieval_handles_project_examples():
    examples = {
        "Explain supplier allocation capacity rules": "multi-supplier allocation",
        "How does RFQ normalization work?": "RFQ processing",
        "What is canonical USD and INR display?": "currency and unit governance",
        "Explain ESG and innovation intelligence": "financial ESG and innovation intelligence",
        "What are project limitations?": "governance limitations and deferred capabilities",
    }
    for question, expected_topic in examples.items():
        matches = search_project_knowledge(question)
        assert matches
        assert expected_topic in {item["topic"] for item in matches}


def test_external_prediction_fails_closed_without_fabrication():
    response = answer_question("Predict PET resin prices for next month", _presentation())
    assert response["intent"] == "unavailable"
    assert response["evidence_available"] is False
    assert "did not browse" in response["answer"]
    assert "fabricate" in response["answer"]
    assert response["external_retrieval_used"] is False
    assert response["action_executed"] is False


def test_limitations_disclose_no_web_or_autonomous_authority():
    response = answer_question("Can you browse the web or approve a supplier?", _presentation())
    assert response["intent"] == "limitations"
    assert "No web browsing" in response["answer"]
    assert "Human approval" in response["answer"]


def test_widget_uses_compact_fixed_panel_and_persistent_session_history():
    source = Path("modules/sourcemate_conversation_ui.py").read_text(encoding="utf-8")
    shell = Path("modules/sourcemate_application_shell.py").read_text(encoding="utf-8")
    explorer = Path("pages/8_Governed_Calculation_Explorer.py").read_text(encoding="utf-8")
    erp_page = Path("pages/9_ERP_Upload_Preview.py").read_text(encoding="utf-8")
    assert "sourcemate_widget_launcher" in source
    assert "sourcemate_widget_panel" in source
    assert "position: fixed" in source
    assert "max-height: min(54vh, 620px)" in source
    assert "max-height: 48vh" in source
    assert "@media (max-width: 640px)" in source
    assert "overflow-y: auto" in source
    assert "background: #161d27" in source
    assert "background: #1b2635" in source
    assert "st.session_state" in source
    assert '_OPEN_KEY = "sourcemate_widget_open"' in source
    assert "sourcemate_pending_question" not in source
    assert "st.form(" in source
    assert "st.text_input(" in source
    assert 'placeholder="Ask SourceMate…"' in source
    assert "st.form_submit_button(\"Send\"" in source
    assert "render_sourcemate_conversation" in shell
    assert "mount_global_sourcemate" in explorer
    assert "mount_global_sourcemate" in erp_page
    assert "render_sourcemate_conversation(presentation)" not in explorer


def test_widget_prioritizes_conversation_and_progressive_disclosure():
    source = Path("modules/sourcemate_conversation_ui.py").read_text(encoding="utf-8")
    assert 'markdown("#### SourceMate")' in source
    assert "SourceMate — Project Assistant" not in source
    assert "Ask about live supplier results" not in source
    assert "The panel stays open after Send" not in source
    assert "✕ Close SourceMate" not in source
    assert 'st.expander("ⓘ Details & controls"' in source
    assert "SOURCEMATE_CONVERSATION_CONTRACT" in source
    assert "Clear conversation" in source
    assert "Human review required" in source
    assert "Evidence: " in source
    assert "on_click=_open_panel" in source
    assert "on_click=_close_panel" in source
    assert "Ask a question about the evidence available on this page." in source


def test_starter_prompts_are_removed_and_display_answers_are_compacted_only_in_ui():
    source = Path("modules/sourcemate_conversation_ui.py").read_text(encoding="utf-8")
    service = Path("modules/sourcemate_conversation.py").read_text(encoding="utf-8")
    assert "def _starter_prompts(" not in source
    assert "sourcemate_starter_prompts" not in source
    assert "Explain the current recommendation" not in source
    assert "Compare the top suppliers" not in source
    assert "What risks need human review?" not in source
    assert "def _compact_answer_for_display(" in source
    assert 'text.replace("Verified project evidence — ", "")' in source
    assert "answer_question(question_to_answer, current_context())" in source
    assert "def answer_question(" in service


def test_no_prohibited_external_or_action_dependencies_are_introduced():
    service = Path("modules/sourcemate_conversation.py").read_text(encoding="utf-8")
    registry = Path("modules/sourcemate_project_knowledge.py").read_text(encoding="utf-8")
    combined = (service + registry).lower()
    assert "import requests" not in combined
    assert "import openai" not in combined
    assert "vector database" not in service.lower()
    assert '"external_retrieval_used": false' in service.lower()
    assert '"action_executed": false' in service.lower()
