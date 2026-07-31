from pathlib import Path


CLOSURE = Path("docs/C2_FLEXIBLE_LAMINATES_CLOSURE.md")
LEDGER = Path("docs/C2_ACTIVITY_DECISION_LEDGER.md")


def test_c2_closure_documents_exist():
    assert CLOSURE.is_file()
    assert LEDGER.is_file()


def test_c2_closure_records_governed_scope():
    text = CLOSURE.read_text(encoding="utf-8")
    required = [
        "PET / PE",
        "PET / MetPET / PE",
        "BOPP / CPP",
        "kg only",
        "USD/kg",
        "compounded process loss",
        "tooling amortisation",
        "Generic supplier risk",
        "technically eligible",
        "Standard allocation",
        "Optimized allocation",
        "Base Case",
        "Polymer Index +20%",
        "MetPET Availability Stress",
        "Adhesive and Conversion Cost +15%",
        "Demand +25%",
        "Press and Lamination Capacity Stress",
        "Tooling Replacement Scenario",
        "allow_nan=False",
        "SourceMate",
        "Calculation & Assumption Explorer",
    ]
    for phrase in required:
        assert phrase in text


def test_c2_closure_preserves_claim_boundaries():
    text = CLOSURE.read_text(encoding="utf-8").lower()
    for phrase in [
        "synthetic demonstration data only",
        "no erp write-back",
        "no autonomous supplier approval",
        "no realized-savings claim",
        "not production reliability",
    ]:
        assert phrase in text


def test_c2_ledger_records_frozen_governance():
    text = LEDGER.read_text(encoding="utf-8")
    assert "2d6323c0b78d560669dd054a9b7e25ce75a06368" in text
    assert "agent/category-expansion-c2-flexible-laminates" in text
    assert "PR remains draft" in text
    assert "S1 and C1 records remain frozen" in text
    assert "No merge, tag, release" in text
