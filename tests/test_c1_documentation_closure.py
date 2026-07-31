"""Integrity checks for the controlled C1 documentation closure."""

from pathlib import Path


CLOSURE = Path("docs/C1_KRAFT_PAPER_CLOSURE.md")
LEDGER = Path("docs/C1_ACTIVITY_LEDGER.md")
REQUIRED_BRANCH = "agent/category-expansion-c1-kraft-paper"
REQUIRED_IMPLEMENTATION_HEAD = "626f33742480e5a6f9f5c9cd5b0f085927e0a666"
REQUIRED_BASE = "ce7c6d09aaa8b022c3de35da1800b94b9dcd7670"


def _text(path: Path) -> str:
    assert path.exists(), f"Missing controlled documentation file: {path}"
    return path.read_text(encoding="utf-8")


def test_c1_closure_records_controlled_repository_coordinates():
    content = _text(CLOSURE)
    assert REQUIRED_BRANCH in content
    assert REQUIRED_IMPLEMENTATION_HEAD in content
    assert REQUIRED_BASE in content
    assert "PR #31" in content
    assert "open, draft, unmerged" in content


def test_c1_closure_records_final_quality_evidence():
    content = _text(CLOSURE)
    for value in (
        "493 passed",
        "30614642110",
        "91104910011",
        "Python compilation: passed",
        "Canonical Streamlit smoke test: passed",
        "one pre-existing pandas FutureWarning",
    ):
        assert value in content


def test_c1_closure_records_scope_and_claim_boundaries():
    content = _text(CLOSURE)
    for value in (
        "Recycled Kraft",
        "Virgin Kraft",
        "Paper Price +20%",
        "Mill / Fibre Continuity Stress",
        "Technical Eligibility",
        "500,000 kg (500 metric tonnes)",
        "no production deployment",
        "no live ERP integration or write-back",
        "no autonomous sourcing, supplier approval or award",
        "no realized savings",
        "Human procurement and technical approval remain mandatory",
    ):
        assert value in content


def test_c1_activity_ledger_preserves_historical_records_and_future_gates():
    content = _text(LEDGER)
    for value in (
        REQUIRED_BRANCH,
        REQUIRED_IMPLEMENTATION_HEAD,
        REQUIRED_BASE,
        "Historical S1 documents are not modified",
        "Final ready-for-review audit",
        "Pending",
        "PR #31 must remain draft",
        "Not authorized",
    ):
        assert value in content


def test_c1_closure_documents_residual_limitations_without_certification_claims():
    content = _text(CLOSURE)
    for value in (
        "Wide supplier tables require internal horizontal scrolling",
        "all-suppliers-technically-ineligible",
        "Formal accessibility and browser-device certification remain outside portfolio scope",
    ):
        assert value in content
    assert "formal WCAG or device certification" in content
