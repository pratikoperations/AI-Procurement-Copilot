from pathlib import Path

from modules.sourcemate_conversation import (
    SOURCEMATE_CONVERSATION_CONTRACT,
    SUPPORTED_INTENTS,
    answer_question,
    classify_intent,
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


def test_contract_and_supported_intents_are_bounded():
    assert SOURCEMATE_CONVERSATION_CONTRACT == "AIPC-SOURCEMATE-CONVERSATIONAL-BIV-1.0"
    assert SUPPORTED_INTENTS == (
        "calculation",
        "assumptions",
        "trace",
        "reconciliation",
        "evidence",
        "limitations",
        "help",
    )


def test_intent_routing_is_deterministic():
    assert classify_intent("What assumptions were used?") == "assumptions"
    assert classify_intent("Show the calculation trace") == "trace"
    assert classify_intent("Are there any mismatches?") == "reconciliation"
    assert classify_intent("What evidence coverage exists?") == "evidence"
    assert classify_intent("Can you browse the web?") == "limitations"
    assert classify_intent("What is the target cost result?") == "calculation"
    assert classify_intent("Tell me something unrelated") == "help"


def test_calculation_answer_labels_verified_and_generated_content():
    response = answer_question("What is the result?", _presentation())
    assert response["intent"] == "calculation"
    assert "Verified evidence:" in response["answer"]
    assert "1.27" in response["answer"]
    assert "Generated explanation:" in response["answer"]
    assert response["external_retrieval_used"] is False
    assert response["action_executed"] is False
    assert response["human_review_required"] is True


def test_assumption_trace_reconciliation_and_evidence_answers_use_current_objects():
    presentation = _presentation()
    assert "annual_volume" in answer_question("assumptions", presentation)["answer"]
    assert "trace-1" in answer_question("trace", presentation)["answer"]
    assert "1 exact match" in answer_question("reconciliation", presentation)["answer"]
    assert "adapter_backed" in answer_question("evidence coverage", presentation)["answer"]


def test_missing_evidence_fails_closed_without_reconstruction():
    presentation = _presentation()
    presentation["calculation_trace"] = {"available": False}
    response = answer_question("show trace", presentation)
    assert response["evidence_available"] is False
    assert "cannot reconstruct" in response["answer"]


def test_limitations_disclose_no_web_or_autonomous_authority():
    response = answer_question("What can you not do?", _presentation())
    assert response["intent"] == "limitations"
    assert "No web browsing" in response["answer"]
    assert "Human approval" in response["answer"]


def test_streamlit_ui_uses_chat_contract_and_session_only_history():
    source = Path("modules/sourcemate_conversation_ui.py").read_text(encoding="utf-8")
    page = Path("pages/8_Governed_Calculation_Explorer.py").read_text(encoding="utf-8")
    assert "st.chat_input(" in source
    assert "st.chat_message(" in source
    assert "st.session_state" in source
    assert "Clear conversation" in source
    assert "does not browse the web" in source
    assert "render_sourcemate_conversation(presentation)" in page


def test_no_prohibited_external_or_action_dependencies_are_introduced():
    service = Path("modules/sourcemate_conversation.py").read_text(encoding="utf-8")
    assert "requests" not in service
    assert "openai" not in service.lower()
    assert "vector" not in service.lower()
    assert "execute" in service.lower()
    assert "external_retrieval_used\": False" in service
    assert "action_executed\": False" in service
