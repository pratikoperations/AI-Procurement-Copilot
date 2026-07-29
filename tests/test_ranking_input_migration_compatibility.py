from __future__ import annotations

from pathlib import Path

from modules.ranking_input_contract import FROZEN_URN, load_contract_bundle
from modules.rfq_workbook_adapter import AdapterResult


def test_contract_routing_preserves_v130_and_adds_v131_locally():
    frozen = load_contract_bundle("1.3.0")
    additive = load_contract_bundle("1.3.1")
    assert frozen.approved_sheets == ("RFQ_QUOTES", "PO_HISTORY", "UPLOAD_METADATA")
    assert "SUPPLIER_RANKING_INPUTS" not in frozen.approved_sheets
    assert additive.approved_sheets[-1] == "SUPPLIER_RANKING_INPUTS"
    assert additive.schema["x-local-schema-registry"]["network_resolution"] is False
    assert FROZEN_URN in additive.schema["x-local-schema-registry"]["resources"]
    assert additive.validator is not None


def test_extended_adapter_result_is_backward_compatible_by_default():
    result = AdapterResult(
        filename="x.xlsx", mode="QUICK_RFQ", schema_version="1.3.0",
        alias_registry_version="1.3.0", upload_file_hash_sha256="a" * 64,
        source_file_hash_sha256=None, selected_sourcing_event_id=None,
        available_sourcing_event_ids=(), rfq_quotes=(), po_history=(),
        upload_metadata=None, mapping_reviews=(), findings=(),
    )
    assert result.supplier_ranking_inputs == ()
    assert result.ranking_evidence_results == ()
    assert result.ranking_scope_matches == ()
    assert result.ranking_mode_eligibility == ()


def test_build_e_review_only_and_blocker_contracts_remain_unchanged():
    controller = Path("modules/rfq_integration_controller.py").read_text(encoding="utf-8")
    compatibility = Path("modules/rfq_legacy_compatibility.py").read_text(encoding="utf-8")
    assert "dataframe=None" in controller
    assert "analysis_handoff_allowed=False" in controller
    assert "handoff_confirmed=False" in controller
    assert "GOVERNED_RANKING_INPUTS_NOT_CANONICAL" in compatibility
