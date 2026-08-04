from modules.sourcemate_conversation import answer_question
from modules import sourcemate_project_knowledge as knowledge
from modules.sourcemate_project_knowledge import search_project_knowledge


def _presentation():
    return {
        "calculation_overview": {},
        "assumptions": [],
        "calculation_trace": {"available": False},
        "reconciliation": {"available": False},
        "sourcemate": {"limitations": ["No web browsing.", "Human approval remains mandatory."]},
    }


def test_esg_question_expands_acronym_and_explains_dimensions():
    response = answer_question("What ESG stands for?", _presentation())
    assert response["intent"] == "project_knowledge"
    assert "Environmental, Social and Governance" in response["answer"]
    assert "| Environmental |" in response["answer"]
    assert "| Social |" in response["answer"]
    assert "| Governance |" in response["answer"]


def test_srm_answer_uses_structured_weight_and_classification_tables():
    response = answer_question("Vendor SRM scores criteria", _presentation())
    assert response["intent"] == "project_knowledge"
    assert "| Particular | Weight |" in response["answer"]
    assert "| Supplier performance | 25% |" in response["answer"]
    assert "| Risk score | 20% |" in response["answer"]
    assert "| Classification | Governed rule |" in response["answer"]
    assert "| Strategic |" in response["answer"]
    assert "| Exit Candidate |" in response["answer"]


def test_flexible_laminates_vendor_question_returns_qualified_suppliers():
    response = answer_question("Which vendor qualified for flexibles?", _presentation())
    assert response["intent"] == "project_knowledge"
    assert "Precision Flexibles Ltd" in response["answer"]
    assert "BarrierPack Films" in response["answer"]
    assert "Circular Laminate Solutions" in response["answer"]
    assert "Eligible" in response["answer"]
    assert "Ineligible" in response["answer"]
    assert "synthetic portfolio records" in response["answer"]
    assert "modules/data_loader.py::get_flexible_laminate_demo_suppliers" in response["evidence_references"]


def test_flexibles_supplier_topic_has_highest_retrieval_priority():
    matches = search_project_knowledge("Which vendor qualified for flexible laminates RFQ?")
    assert matches
    assert matches[0]["topic"] == "flexible laminates supplier qualification"


def test_flexibles_participant_count_returns_exact_supplier_evidence_not_generic_rfq_text():
    response = answer_question("How many vendors participated in flexibles RFQ?", _presentation())
    assert response["intent"] == "project_knowledge"
    assert "contains three participating suppliers" in response["answer"]
    assert "Precision Flexibles Ltd" in response["answer"]
    assert "BarrierPack Films" in response["answer"]
    assert "Circular Laminate Solutions" in response["answer"]
    assert "The RFQ layer ingests" not in response["answer"]


def test_kraft_vendor_quote_and_tco_question_returns_specific_table_and_current_page_boundary():
    response = answer_question(
        "Which vendor approved for kraft paper. What is his RFQ quote rate vs TCO rate?",
        _presentation(),
    )
    assert response["intent"] == "project_knowledge"
    assert "Western Fibre Mills" in response["answer"]
    assert "National Kraft Industries" in response["answer"]
    assert "Circular Paperworks Ltd" in response["answer"]
    assert "USD 0.840/kg" in response["answer"]
    assert "USD 0.960/kg" in response["answer"]
    assert "USD 0.800/kg" in response["answer"]
    assert "TCO evidence status" in response["answer"]
    assert "not published by this cross-category should-cost view" in response["answer"]
    assert "has not calculated or inferred TCO" in response["answer"]
    assert "does not approve or award" in response["answer"]
    assert "Unavailable in the static cross-category registry" not in response["answer"]
    assert "The RFQ layer ingests" not in response["answer"]


def test_kraft_specific_topic_has_priority_over_generic_rfq_and_tco_topics():
    matches = search_project_knowledge("kraft paper RFQ quote rate vs TCO rate")
    assert matches
    assert matches[0]["topic"] == "kraft paper controlled supplier evidence"


def test_flexibles_quotes_follow_selected_inr_display_currency(monkeypatch):
    monkeypatch.setattr(
        knowledge,
        "_session_display_context",
        lambda: ("INR", 83.0, "Governed Calculation Explorer"),
    )
    response = answer_question("How many vendors participated in flexibles RFQ?", _presentation())
    assert "INR 170.15/kg" in response["answer"]
    assert "INR 180.36/kg" in response["answer"]
    assert "INR 159.94/kg" in response["answer"]
    assert "USD 2.050/kg" not in response["answer"]
    assert "83.00 INR/USD" in response["answer"]


def test_kraft_quotes_support_both_display_currencies(monkeypatch):
    monkeypatch.setattr(
        knowledge,
        "_session_display_context",
        lambda: ("BOTH", 83.0, "Governed Calculation Explorer"),
    )
    response = answer_question("kraft paper RFQ quote rate vs TCO rate", _presentation())
    assert "USD 0.840/kg / INR 69.72/kg" in response["answer"]
    assert "USD 0.960/kg / INR 79.68/kg" in response["answer"]
    assert "USD 0.800/kg / INR 66.40/kg" in response["answer"]


def test_inr_selection_without_valid_fx_fails_closed_to_canonical_usd(monkeypatch):
    monkeypatch.setattr(
        knowledge,
        "_session_display_context",
        lambda: ("INR", None, "Governed Calculation Explorer"),
    )
    response = answer_question("Which vendor qualified for flexibles?", _presentation())
    assert "USD 2.050/kg" in response["answer"]
    assert "INR conversion is unavailable" in response["answer"]
    assert "has not calculated or inferred" in response["answer"]
