"""Governed Calculation Explorer and SourceMate Basic View assurance."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
from datetime import date
from pathlib import Path

from modules.calculation_explorer_adapter import build_explorer_payload
from modules.calculation_explorer_presenter import (
    EXPLORER_PRESENTATION_CONTRACT_VERSION,
    GOVERNANCE_DISCLOSURES,
    build_governed_explorer_presentation,
)
from modules.calculation_reconciliation_gate3 import reconcile_trace
from modules.calculation_trace_adapters import build_should_cost_trace
from modules.reconciliation_coverage import ADAPTER_BACKED_COVERAGE_IDS, adapter_coverage_classification
from modules.sourcemate_presenter import SOURCEMATE_CONTRACT_VERSION, build_sourcemate_summary


def _payload(result=None):
    result = result or {"components": {"paper": 1.0, "conversion": 0.2}, "target_unit_cost_usd": 1.2, "unit": "USD/unit"}
    assumptions = {
        "category": "Corrugated Board",
        "annual_volume": 500000,
        "annual_volume_unit": "unit",
        "uncatalogued_demo_value": "disclosed",
    }
    return build_explorer_payload(
        context={"mode": "read_only"},
        assumptions=assumptions,
        authoritative_results={"COR-001": result},
        supplied_keys=("annual_volume",),
        derived_keys=("annual_volume_unit",),
    )


def _presentation():
    result = {"components": {"paper": 1.0, "conversion": 0.2}, "target_unit_cost_usd": 1.2, "unit": "USD/unit"}
    trace = build_should_cost_trace(
        calculation_id="COR-001",
        formula_id="F-PKG-SHOULDCOST",
        category="Corrugated Board",
        inputs={"mode": "test"},
        authoritative_result=result,
    )
    reconciliation = reconcile_trace(
        trace=trace,
        authoritative_service="calculate_packaging_should_cost",
        authoritative_output=result,
        calculation_id="COR-001",
        formula_id="F-PKG-SHOULDCOST",
        formula_version="1.0",
        compared_fields=("",),
        repeated_trace_id=trace.trace_id,
    )
    return build_governed_explorer_presentation(
        explorer_payload=_payload(result),
        calculation_id="COR-001",
        coverage_id="REC-COR",
        trace=asdict(trace),
        reconciliation=asdict(reconciliation),
    )


def test_presenter_contract_is_stable_read_only_and_non_executable():
    presentation = _presentation()
    assert presentation["contract_version"] == EXPLORER_PRESENTATION_CONTRACT_VERSION
    assert set(presentation) >= {
        "context", "calculation_overview", "assumptions", "trace_summary",
        "reconciliation_summary", "sourcemate", "human_review_checklist",
        "governance_disclosures",
    }
    assert presentation["read_only"] is True
    assert presentation["approval_persistence"] is False
    assert presentation["autonomous_award"] is False
    assert presentation["human_review_required"] is True
    assert presentation["calculation_overview"]["formula_executable"] is False
    assert tuple(presentation["governance_disclosures"]) == GOVERNANCE_DISCLOSURES


def test_presenter_does_not_mutate_explorer_trace_or_reconciliation_sources():
    payload = _payload()
    original_payload = deepcopy(payload)
    result = payload["calculations"][0]["result"]
    trace = build_should_cost_trace(
        calculation_id="COR-001", formula_id="F-PKG-SHOULDCOST",
        category="Corrugated Board", inputs={"mode": "test"}, authoritative_result=result,
    )
    reconciliation = reconcile_trace(
        trace=trace, authoritative_service="calculate_packaging_should_cost",
        authoritative_output=result, calculation_id="COR-001", formula_id="F-PKG-SHOULDCOST",
        formula_version="1.0", compared_fields=("",), repeated_trace_id=trace.trace_id,
    )
    trace_record = asdict(trace); reconciliation_record = asdict(reconciliation)
    original_trace = deepcopy(trace_record); original_reconciliation = deepcopy(reconciliation_record)
    build_governed_explorer_presentation(
        explorer_payload=payload, calculation_id="COR-001", coverage_id="REC-COR",
        trace=trace_record, reconciliation=reconciliation_record,
    )
    assert payload == original_payload
    assert trace_record == original_trace
    assert reconciliation_record == original_reconciliation


def test_provenance_and_uncatalogued_assumptions_remain_visible():
    presentation = _presentation()
    by_key = {item["key"]: item for item in presentation["assumptions"]}
    assert by_key["annual_volume"]["status"] == "supplied"
    assert by_key["annual_volume_unit"]["status"] == "derived"
    assert by_key["uncatalogued_demo_value"]["category"] == "Uncatalogued"
    assert by_key["uncatalogued_demo_value"]["evidence_classification"]
    assert by_key["uncatalogued_demo_value"]["governance_caveat"] == "Uncatalogued value; human review required."


def test_adapter_backed_route_displays_trace_and_reconciliation():
    presentation = _presentation()
    assert presentation["sourcemate"]["coverage_classification"] == "adapter_backed"
    assert presentation["trace_summary"]["available"] is True
    assert presentation["reconciliation_summary"]["classification"] == "exact_match"
    assert presentation["reconciliation_summary"]["blocking_status"] == "clear"
    assert presentation["reconciliation_summary"]["human_review_status"] == "required"
    assert ADAPTER_BACKED_COVERAGE_IDS == {
        "REC-PET", "REC-KRF", "REC-COR", "REC-LAM", "REC-STL", "REC-SCORE-GEN", "REC-ELG"
    }


def test_deferred_route_is_disclosed_without_fabricated_trace():
    payload = build_explorer_payload(
        context={"mode": "read_only"},
        assumptions={"category": "Packaging", "annual_volume": 500000},
        authoritative_results={"TCO-001": {"adjusted_tco": 100.0}},
    )
    presentation = build_governed_explorer_presentation(
        explorer_payload=payload,
        calculation_id="TCO-001",
        coverage_id="REC-TCO-PKG",
    )
    assert adapter_coverage_classification("REC-TCO-PKG") == "unsupported_deferred_coverage"
    assert presentation["trace_summary"]["available"] is False
    assert presentation["reconciliation_summary"]["classification"] == "unsupported_deferred_coverage"
    assert presentation["sourcemate"]["dedicated_adapter_deferred"] is True
    assert presentation["sourcemate"]["adapter_reconciled"] is False
    assert presentation["human_review_required"] is True


def test_sourcemate_retains_evidence_locations_and_flags_review_expiry():
    calculation = _payload()["calculations"][0]
    assumptions = [{
        "assumption_id": "ASM-TEST", "key": "annual_volume",
        "evidence_classification": "supplier_or_rfq_supplied",
        "source_reference": "controlled-test-reference",
        "source_level": "rfq_scenario", "review_expiry_date": "2025-01-01",
    }]
    original_calculation = deepcopy(calculation); original_assumptions = deepcopy(assumptions)
    summary = build_sourcemate_summary(
        calculation=calculation,
        assumptions=assumptions,
        coverage_id="REC-COR",
        runtime_evidence={"EXP-EV-002": "present in generated package"},
        today=date(2026, 8, 1),
    )
    assert summary["contract_version"] == SOURCEMATE_CONTRACT_VERSION
    assert summary["external_verification_claimed"] is False
    assert summary["human_review_required"] is True
    assert any(row["evidence_id"] == "EXP-EV-002" for row in summary["export_evidence"])
    assert next(row for row in summary["export_evidence"] if row["evidence_id"] == "EXP-EV-002")["runtime_presence"] == "present in generated package"
    assert summary["assumption_sources"][0]["review_due"] is True
    assert calculation == original_calculation and assumptions == original_assumptions


def test_ui_and_page_are_read_only_and_contain_required_sections_and_disclosures():
    ui_source = Path("modules/calculation_explorer_ui.py").read_text(encoding="utf-8")
    page_source = Path("pages/8_Governed_Calculation_Explorer.py").read_text(encoding="utf-8")
    for section in ("Overview", "Assumptions", "Calculation Trace", "Reconciliation", "SourceMate", "Human Review"):
        assert section in ui_source
    for prohibited in ("st.button(", "st.number_input(", "st.text_input(", "st.form(", "st.download_button("):
        assert prohibited not in ui_source
        assert prohibited not in page_source
    assert "formula metadata is documentation only" in page_source.lower()
    assert "human approval remains mandatory" in page_source.lower()
    assert "no autonomous award" in page_source.lower()
    assert "unsupported_deferred_coverage" not in page_source  # classification comes from the governed registry
    assert "st.radio" in ui_source and "horizontal=True" in ui_source
