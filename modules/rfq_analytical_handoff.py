"""Strict governed bridge from C2 evidence to the frozen analytical engines."""
from __future__ import annotations

from dataclasses import asdict
from datetime import date
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
from typing import Any, Callable, Mapping, Sequence

import pandas as pd

from modules.rfq_handoff_models import (
    AnalyticalHandoffManifest,
    AnalyticalHandoffResult,
    EngineExecutionResult,
    EngineStageResult,
    ENGINE_STAGES,
    HANDOFF_CONTRACT_VERSION,
    HANDOFF_DIGEST_VERSION,
    HANDOFF_MANIFEST_VERSION,
    HandoffFieldManifest,
    HandoffSupplierManifest,
)
from modules.rfq_review_state import stable_digest
from modules.rfq_workbook_adapter import Finding

RANKING_MAPPING = {
    "OTIF_PERCENT": "OTIF %",
    "QUALITY_PPM": "Quality PPM",
    "SUPPLIER_AUDIT_SCORE": "Audit Score",
    "COMPLAINT_RATE_PERCENT": "Complaint Rate %",
    "CAPACITY_BUFFER_PERCENT": "Capacity Buffer %",
    "RECYCLABILITY_PERCENT": "Recyclability",
    "CERTIFICATION_SCORE": "Certification",
    "CARBON_SCORE": "Carbon Score",
    "EPR_READINESS_SCORE": "EPR Readiness",
    "PCR_CONTENT_PERCENT": "PCR Content %",
}
DATAFRAME_COLUMNS = (
    "Supplier", "Supplier ID", "Sourcing Event ID", "RFQ Number", "RFQ Item",
    "Quotation Version", "Quotation Source Row ID", "Ranking Record ID",
    "Ranking Input Version", "Ranking Scope", "Ranking Measurement End",
    "Comparison UOM", "Quoted Unit Price USD", "MOQ", "Lead Time Days",
    "Payment Terms", "Incoterms", *RANKING_MAPPING.values(),
)
ANALYTICAL_ASSUMPTION_KEYS = {
    "annual_volume", "max_supplier_share", "min_backup_share", "min_risk_score",
    "min_esg_score", "carrying_cost_rate", "freight_rate", "duty_rate",
    "insurance_rate", "quality_cost_rate", "target_unit_cost_usd", "category",
    "commodity", "category_profile", "annual_volume_unit",
}


def filter_analytical_assumptions(values: Mapping[str, Any] | None) -> dict[str, Any]:
    """Return only assumptions capable of affecting analytical outputs."""
    source = values or {}
    return {key: source[key] for key in sorted(ANALYTICAL_ASSUMPTION_KEYS) if key in source}


def _decimal(value: Any) -> Decimal | None:
    try:
        if value is None or str(value).strip() == "":
            return None
        result = Decimal(str(value))
        return result if result.is_finite() else None
    except (InvalidOperation, ValueError, TypeError):
        return None


def _finding(
    severity: str,
    code: str,
    message: str,
    row: int | None = None,
    field: str | None = None,
) -> Finding:
    return Finding(severity, code, message, "E2_ANALYTICAL_HANDOFF", row, field)


def _payment_terms(values: Mapping[str, Any]) -> tuple[str | None, str | None, str | None]:
    days = values.get("PAYMENT_DAYS")
    if isinstance(days, int) and not isinstance(days, bool) and days >= 0:
        return (
            "Immediate" if days == 0 else f"Net {days}",
            "PAYMENT_DAYS",
            "PAYMENT_DAYS_TO_DISPLAY",
        )
    return None, None, None


def _canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")


def _selected_quotes(orchestration_result: Any, rfq_number: str, rfq_item: str) -> list[Any]:
    return [
        item
        for item in orchestration_result.enriched_quotes
        if item.eligible_for_analysis
        and str(item.record.canonical_values.get("RFQ_NUMBER")) == str(rfq_number)
        and str(item.record.canonical_values.get("RFQ_ITEM")) == str(rfq_item)
    ]


def build_analytical_handoff(
    adapter_result: Any,
    orchestration_result: Any,
    *,
    selected_sourcing_event_id: str,
    selected_rfq_number: str,
    selected_rfq_item: str,
    evaluation_date: date,
    analytical_assumptions: Mapping[str, Any] | None = None,
    approval_digests: Mapping[str, str] | None = None,
) -> AnalyticalHandoffResult:
    """Build a canonical USD DataFrame only when every E2 gate passes."""
    assumptions = filter_analytical_assumptions(analytical_assumptions)
    approvals = dict(approval_digests or {})
    blockers: list[str] = []
    findings: list[Finding] = []
    metadata = adapter_result.upload_metadata or {}
    schema_version = str(metadata.get("SCHEMA_VERSION") or "")
    upload_mode = str(adapter_result.mode or metadata.get("UPLOAD_MODE") or "")
    if schema_version != "1.3.1":
        blockers.append("V130_ANALYTICAL_HANDOFF_PROHIBITED")
    if upload_mode != "FULL_SOURCING_REVIEW":
        blockers.append("FULL_REVIEW_REQUIRED_FOR_ANALYTICAL_HANDOFF")

    quotes = _selected_quotes(orchestration_result, selected_rfq_number, selected_rfq_item)
    quote_suppliers = [str(item.record.canonical_values.get("SUPPLIER_ID") or "") for item in quotes]
    if len(quotes) < 2:
        blockers.append("MINIMUM_ELIGIBLE_SUPPLIER_COUNT_NOT_MET")
    if any(not supplier for supplier in quote_suppliers) or len(set(quote_suppliers)) != len(quote_suppliers):
        blockers.append("DUPLICATE_HANDOFF_SUPPLIER")

    eligibility = {
        item.supplier_id: item
        for item in adapter_result.ranking_mode_eligibility
        if item.mode == "FULL_SOURCING_REVIEW"
        and item.rfq_number == str(selected_rfq_number)
        and item.rfq_item == str(selected_rfq_item)
        and item.status == "RANKING_REVIEW_COMPLETE"
    }
    if set(quote_suppliers) != set(eligibility):
        blockers.append("SUPPLIER_SET_MISMATCH")
    matches = {
        item.supplier_id: item
        for item in adapter_result.ranking_scope_matches
        if item.rfq_number == str(selected_rfq_number)
        and item.rfq_item == str(selected_rfq_item)
    }
    evidence_by_record: dict[str, dict[str, Any]] = {}
    for item in adapter_result.ranking_evidence_results:
        evidence_by_record.setdefault(item.ranking_record_id, {})[item.canonical_field] = item

    rows: list[dict[str, Any]] = []
    manifests: list[HandoffSupplierManifest] = []
    comparison_uoms: set[str] = set()
    for quote in sorted(quotes, key=lambda item: str(item.record.canonical_values.get("SUPPLIER_ID") or "")):
        values = quote.record.canonical_values
        supplier_id = str(values.get("SUPPLIER_ID") or "")
        row_number = quote.record.provenance.source_row_number
        match = matches.get(supplier_id)
        row_blockers: list[str] = []
        if (
            match is None
            or not match.eligible
            or match.reason != "MATCHED"
            or match.fallback_record_id is not None
            or not match.ranking_record_id
        ):
            row_blockers.append("RANKING_MATCH_NOT_ELIGIBLE")
        field_results = (
            {}
            if match is None or not match.ranking_record_id
            else evidence_by_record.get(match.ranking_record_id, {})
        )
        if set(field_results) != set(RANKING_MAPPING):
            row_blockers.append("RANKING_FIELD_RESULT_MISSING")
        elif any(field_results[name].canonical_evidence_status != "VALID" for name in RANKING_MAPPING):
            row_blockers.append("RANKING_FIELD_NOT_VALID_FOR_HANDOFF")

        normalized = quote.normalization.normalized_values
        if str(normalized.get("COMPARISON_CURRENCY") or "").upper() != "USD":
            row_blockers.append("USD_ANALYTICAL_BASIS_REQUIRED")
        price = _decimal(normalized.get("NORMALIZED_UNIT_PRICE"))
        moq = _decimal(values.get("MINIMUM_ORDER_QUANTITY"))
        lead = values.get("LEAD_TIME_DAYS")
        incoterm = str(values.get("INCOTERMS_CODE") or "").strip().upper()
        payment, payment_source, payment_transform = _payment_terms(values)
        comparison_uom = str(normalized.get("COMPARISON_UOM") or "").strip()
        comparison_uoms.add(comparison_uom)
        if price is None or price <= 0:
            row_blockers.append("NORMALIZED_USD_PRICE_REQUIRED")
        if moq is None or moq <= 0:
            row_blockers.append("MOQ_REQUIRED_FOR_HANDOFF")
        if not isinstance(lead, int) or isinstance(lead, bool) or lead < 0:
            row_blockers.append("LEAD_TIME_REQUIRED_FOR_HANDOFF")
        if payment is None:
            row_blockers.append("PAYMENT_DAYS_REQUIRED_FOR_HANDOFF")
        if incoterm not in {"DDP", "DAP", "CIF", "FOB", "EXW"}:
            row_blockers.append("INCOTERMS_REQUIRED_FOR_HANDOFF")
        if not comparison_uom:
            row_blockers.append("COMPARISON_UOM_MISMATCH")
        if row_blockers:
            blockers.extend(row_blockers)
            findings.extend(
                _finding("Blocking", code, f"Supplier {supplier_id} blocked by {code}.", row_number)
                for code in row_blockers
            )
            continue

        row = {
            "Supplier": str(values.get("SUPPLIER_NAME") or ""),
            "Supplier ID": supplier_id,
            "Sourcing Event ID": str(values.get("SOURCING_EVENT_ID") or ""),
            "RFQ Number": str(values.get("RFQ_NUMBER") or ""),
            "RFQ Item": str(values.get("RFQ_ITEM") or ""),
            "Quotation Version": int(values.get("QUOTATION_VERSION")),
            "Quotation Source Row ID": quote.record.provenance.source_row_id,
            "Ranking Record ID": match.ranking_record_id,
            "Ranking Input Version": int(match.ranking_input_version or 0),
            "Ranking Scope": str(match.matched_scope or ""),
            "Ranking Measurement End": match.measurement_period_end,
            "Comparison UOM": comparison_uom,
            "Quoted Unit Price USD": float(price),
            "MOQ": float(moq),
            "Lead Time Days": int(lead),
            "Payment Terms": payment,
            "Incoterms": incoterm,
        }
        field_manifest: list[HandoffFieldManifest] = []
        commercial_sources = {
            "Quoted Unit Price USD": ("BUILD_D", "NORMALIZED_UNIT_PRICE", "BUILD_D_NORMALIZATION"),
            "MOQ": ("RFQ_QUOTE", "MINIMUM_ORDER_QUANTITY", "DECIMAL_TO_FLOAT"),
            "Lead Time Days": ("RFQ_QUOTE", "LEAD_TIME_DAYS", None),
            "Payment Terms": ("RFQ_QUOTE", payment_source, payment_transform),
            "Incoterms": ("RFQ_QUOTE", "INCOTERMS_CODE", "UPPERCASE_CANONICAL"),
        }
        for target, (domain, source, transform) in commercial_sources.items():
            field_manifest.append(
                HandoffFieldManifest(
                    target,
                    type(row[target]).__name__,
                    supplier_id,
                    domain,
                    str(source),
                    quote.record.provenance.source_row_id,
                    None,
                    row[target],
                    None,
                    "CANONICAL_OR_NORMALIZED",
                    transform,
                    True,
                )
            )
        for canonical, target in RANKING_MAPPING.items():
            evidence = field_results[canonical]
            row[target] = float(Decimal(str(evidence.canonical_value)))
            field_manifest.append(
                HandoffFieldManifest(
                    target,
                    "float64",
                    supplier_id,
                    "C2_RANKING",
                    canonical,
                    str(evidence.source_reference.get("source_row_id") or ""),
                    evidence.ranking_record_id,
                    evidence.canonical_value,
                    evidence.canonical_evidence_status,
                    str(evidence.value_origin or ""),
                    "CANONICAL_FIELD_RENAME",
                    True,
                )
            )
        rows.append(row)
        manifests.append(
            HandoffSupplierManifest(
                supplier_id,
                row["Supplier"],
                row["Quotation Source Row ID"],
                row["Quotation Version"],
                match.ranking_record_id,
                int(match.ranking_input_version or 0),
                str(match.matched_scope or ""),
                match.measurement_period_end,
                tuple(field_manifest),
            )
        )

    if len(comparison_uoms) != 1 or "" in comparison_uoms:
        blockers.append("COMPARISON_UOM_MISMATCH")
    blockers = list(dict.fromkeys(blockers))
    if blockers:
        findings.extend(
            _finding(
                "Fatal" if code in {"SUPPLIER_SET_MISMATCH", "DUPLICATE_HANDOFF_SUPPLIER"} else "Blocking",
                code,
                f"Analytical handoff blocked by {code}.",
            )
            for code in blockers
            if not any(item.code == code for item in findings)
        )
        return AnalyticalHandoffResult(False, None, None, None, tuple(blockers), (), tuple(findings))

    frame = pd.DataFrame(rows, columns=DATAFRAME_COLUMNS)
    for column in [
        "Supplier", "Supplier ID", "Sourcing Event ID", "RFQ Number", "RFQ Item",
        "Quotation Source Row ID", "Ranking Record ID", "Ranking Scope",
        "Comparison UOM", "Payment Terms", "Incoterms",
    ]:
        frame[column] = frame[column].astype("string")
    for column in ["Quotation Version", "Ranking Input Version", "Lead Time Days"]:
        frame[column] = frame[column].astype("Int64")
    frame["Ranking Measurement End"] = pd.to_datetime(frame["Ranking Measurement End"])
    for column in ["Quoted Unit Price USD", "MOQ", *RANKING_MAPPING.values()]:
        frame[column] = pd.to_numeric(frame[column], errors="raise").astype("float64")
    frame = frame.sort_values("Supplier ID", kind="stable").reset_index(drop=True)
    dataframe_digest = sha256(_canonical_json(frame.to_dict(orient="records"))).hexdigest()
    first_quote = next(iter(adapter_result.rfq_quotes))
    manifest = AnalyticalHandoffManifest(
        HANDOFF_MANIFEST_VERSION,
        HANDOFF_CONTRACT_VERSION,
        str(first_quote.provenance.upload_file_hash_sha256),
        schema_version,
        str(first_quote.provenance.alias_registry_version),
        upload_mode,
        selected_sourcing_event_id,
        selected_rfq_number,
        selected_rfq_item,
        evaluation_date,
        "USD",
        next(iter(comparison_uoms)),
        tuple(manifests),
        stable_digest(assumptions),
        stable_digest(
            {
                "adapter": [getattr(item, "code", "") for item in adapter_result.findings],
                "orchestration": [
                    getattr(item, "code", "")
                    for item in orchestration_result.conditional_findings
                ],
                "approvals": approvals,
            }
        ),
        dataframe_digest,
    )
    digest = sha256(
        _canonical_json(
            {
                "digest_version": HANDOFF_DIGEST_VERSION,
                "manifest": asdict(manifest),
                "approvals": approvals,
            }
        )
    ).hexdigest()
    frame.attrs.update(
        {
            "governed_handoff": True,
            "handoff_contract_version": HANDOFF_CONTRACT_VERSION,
            "handoff_manifest_digest": digest,
            "analytical_currency": "USD",
            "selected_rfq_number": selected_rfq_number,
            "selected_rfq_item": selected_rfq_item,
        }
    )
    findings.append(
        _finding(
            "Information",
            "GOVERNED_ANALYTICAL_HANDOFF_READY",
            "All machine-verifiable E2 controls passed.",
        )
    )
    return AnalyticalHandoffResult(True, frame, manifest, digest, (), (), tuple(findings))


def _supplier_sets(value: Any, *, _seen: set[int] | None = None) -> tuple[tuple[str, ...], ...]:
    """Recursively collect supplier sets from governed structured stage outputs."""
    seen = set() if _seen is None else _seen
    identity = id(value)
    if identity in seen:
        return ()
    seen.add(identity)

    if isinstance(value, pd.DataFrame):
        if "Supplier ID" not in value.columns:
            return ()
        observed = tuple(sorted(str(item) for item in value["Supplier ID"].tolist()))
        return (observed,)

    if isinstance(value, pd.Series):
        if value.name == "Supplier ID":
            observed = tuple(sorted(str(item) for item in value.tolist()))
            return (observed,)
        if "Supplier ID" in value.index:
            return ((str(value["Supplier ID"]),),)
        return ()

    if isinstance(value, Mapping):
        collected: list[tuple[str, ...]] = []
        for nested in value.values():
            collected.extend(_supplier_sets(nested, _seen=seen))
        return tuple(collected)

    if isinstance(value, (list, tuple)):
        collected = []
        for nested in value:
            collected.extend(_supplier_sets(nested, _seen=seen))
        return tuple(collected)

    return ()


def run_engine_stages(
    dataframe: pd.DataFrame,
    handoff_digest: str,
    stage_functions: Mapping[str, Callable[[Mapping[str, Any]], Any]],
) -> EngineExecutionResult:
    """Run frozen-engine callables in order and record deterministic fail-closed evidence."""
    suppliers = tuple(sorted(str(value) for value in dataframe["Supplier ID"].tolist()))
    outputs: dict[str, Any] = {"dataframe": dataframe}
    results: list[EngineStageResult] = []
    blocked = False
    for stage in ENGINE_STAGES:
        if blocked:
            results.append(
                EngineStageResult(
                    stage,
                    "NOT_STARTED",
                    handoff_digest,
                    suppliers,
                    "UPSTREAM_STAGE_BLOCKED",
                    "A prior stage failed.",
                )
            )
            continue
        function = stage_functions.get(stage)
        if function is None:
            results.append(
                EngineStageResult(
                    stage,
                    "BLOCKED",
                    handoff_digest,
                    suppliers,
                    "ENGINE_STAGE_NOT_CONFIGURED",
                    f"No callable configured for {stage}.",
                )
            )
            blocked = True
            continue
        try:
            value = function(outputs)
            for observed in _supplier_sets(value):
                if observed != suppliers:
                    raise ValueError(
                        f"Supplier set changed during {stage}: "
                        f"expected {suppliers}, observed {observed}."
                    )
            outputs[stage] = value
            results.append(EngineStageResult(stage, "PASSED", handoff_digest, suppliers))
        except Exception as exc:
            code = (
                f"{stage}_SUPPLIER_SET_MISMATCH"
                if "Supplier set changed during" in str(exc)
                else f"{stage}_FAILED"
            )
            results.append(
                EngineStageResult(
                    stage,
                    "BLOCKED",
                    handoff_digest,
                    suppliers,
                    code,
                    str(exc),
                )
            )
            blocked = True
    return EngineExecutionResult(not blocked, outputs, tuple(results))
