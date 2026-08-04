from modules.sourcemate_conversation import answer_question
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
