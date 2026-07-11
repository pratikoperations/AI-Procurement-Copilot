"""Intelligent RFQ header recognition, normalization, and diagnostics."""

from __future__ import annotations

import re
from difflib import SequenceMatcher

import pandas as pd

CANONICAL_COLUMNS = {
    "Supplier": ["supplier", "supplier name", "vendor", "vendor name", "bidder", "source"],
    "Quoted Unit Price USD": [
        "quoted unit price usd", "unit price", "quoted price", "price", "rate", "unit rate",
        "price usd", "quoted rate", "landed price",
    ],
    "MOQ": ["moq", "minimum order quantity", "minimum qty", "min order qty", "order minimum"],
    "Lead Time Days": ["lead time days", "lead time", "delivery lead time", "delivery days", "lead days"],
    "Payment Terms": ["payment terms", "payment term", "credit terms", "credit days", "terms of payment"],
    "Incoterms": ["incoterms", "incoterm", "delivery terms", "shipping terms", "trade terms"],
    "OTIF %": ["otif %", "otif", "on time in full", "on-time delivery", "service level"],
    "Quality PPM": ["quality ppm", "ppm", "defect ppm", "rejection ppm", "quality defects"],
    "Audit Score": ["audit score", "supplier audit", "quality audit score", "audit rating"],
    "Complaint Rate %": ["complaint rate %", "complaint rate", "complaints %", "customer complaint rate"],
    "Capacity Buffer %": ["capacity buffer %", "capacity buffer", "spare capacity %", "available capacity %"],
    "Recyclability": ["recyclability", "recyclability score", "recyclable %"],
    "Certification": ["certification", "certification score", "certifications", "compliance score"],
    "Carbon Score": ["carbon score", "carbon rating", "emission score", "co2 score"],
    "EPR Readiness": ["epr readiness", "epr score", "epr compliance"],
    "PCR Content %": ["pcr content %", "pcr content", "recycled content %", "post consumer recycled %"],
    "Supplier Capacity": ["supplier capacity", "capacity", "annual capacity", "available volume"],
    "Currency": ["currency", "currency code", "quote currency"],
    "Unit": ["unit", "uom", "unit of measure", "measurement unit"],
    "Material": ["material", "commodity", "item", "product", "grade"],
    "Plant": ["plant", "location", "site", "supplier location"],
}

UNIT_ALIASES = {
    "kg": "kg", "kgs": "kg", "kilogram": "kg", "kilograms": "kg",
    "mt": "MT", "ton": "MT", "tons": "MT", "tonne": "MT", "tonnes": "MT",
    "pc": "piece", "pcs": "piece", "piece": "piece", "pieces": "piece", "ea": "piece",
    "m": "meter", "meter": "meter", "meters": "meter", "metre": "meter", "metres": "meter",
    "l": "liter", "ltr": "liter", "litre": "liter", "liter": "liter", "liters": "liter",
}


def _clean_header(value: object) -> str:
    text = str(value).strip().lower()
    text = re.sub(r"[_\-\/]+", " ", text)
    text = re.sub(r"[^a-z0-9% ]+", "", text)
    return re.sub(r"\s+", " ", text).strip()


def _best_column_match(header: str, threshold: float = 0.72):
    cleaned = _clean_header(header)
    best_name = None
    best_score = 0.0
    match_type = "unmapped"

    for canonical, aliases in CANONICAL_COLUMNS.items():
        candidates = [canonical, *aliases]
        for alias in candidates:
            alias_clean = _clean_header(alias)
            if cleaned == alias_clean:
                return canonical, 1.0, "exact"
            score = SequenceMatcher(None, cleaned, alias_clean).ratio()
            if score > best_score:
                best_name, best_score = canonical, score

    if best_score >= threshold:
        match_type = "fuzzy"
        return best_name, round(best_score, 3), match_type
    return None, round(best_score, 3), match_type


def detect_column_mapping(columns, threshold: float = 0.72):
    """Return source-to-canonical mapping and confidence diagnostics."""
    mapping = {}
    diagnostics = []
    used_targets = set()

    for source in columns:
        target, confidence, match_type = _best_column_match(source, threshold)
        if target in used_targets:
            diagnostics.append({
                "Source Column": str(source), "Mapped Column": None,
                "Confidence": confidence, "Match Type": "duplicate target",
            })
            continue
        if target:
            mapping[source] = target
            used_targets.add(target)
        diagnostics.append({
            "Source Column": str(source), "Mapped Column": target,
            "Confidence": confidence, "Match Type": match_type,
        })
    return mapping, diagnostics


def normalize_units(series: pd.Series) -> pd.Series:
    """Normalize common unit-of-measure labels while preserving unknown values."""
    def convert(value):
        if pd.isna(value):
            return value
        cleaned = _clean_header(value)
        return UNIT_ALIASES.get(cleaned, str(value).strip())
    return series.map(convert)


def normalize_rfq_dataframe(df: pd.DataFrame):
    """Map RFQ headers to canonical names and return normalized data plus quality report."""
    source_df = df.copy()
    mapping, diagnostics = detect_column_mapping(source_df.columns)
    normalized = source_df.rename(columns=mapping)

    if "Unit" in normalized.columns:
        normalized["Unit"] = normalize_units(normalized["Unit"])

    numeric_columns = [
        "Quoted Unit Price USD", "MOQ", "Lead Time Days", "OTIF %", "Quality PPM",
        "Audit Score", "Complaint Rate %", "Capacity Buffer %", "Recyclability",
        "Certification", "Carbon Score", "EPR Readiness", "PCR Content %", "Supplier Capacity",
    ]
    conversion_issues = {}
    for column in numeric_columns:
        if column in normalized.columns:
            original_non_null = normalized[column].notna()
            converted = pd.to_numeric(normalized[column], errors="coerce")
            bad_count = int((original_non_null & converted.isna()).sum())
            if bad_count:
                conversion_issues[column] = bad_count
            normalized[column] = converted

    duplicate_rows = 0
    duplicate_suppliers = []
    if "Supplier" in normalized.columns:
        supplier_clean = normalized["Supplier"].astype(str).str.strip().str.lower()
        duplicate_mask = supplier_clean.duplicated(keep=False)
        duplicate_rows = int(duplicate_mask.sum())
        duplicate_suppliers = sorted(normalized.loc[duplicate_mask, "Supplier"].astype(str).unique().tolist())

    missing_cells = int(normalized.isna().sum().sum())
    total_cells = max(int(normalized.shape[0] * normalized.shape[1]), 1)
    mapped_count = len(mapping)
    source_count = max(len(source_df.columns), 1)
    mapping_score = mapped_count / source_count
    completeness_score = 1 - (missing_cells / total_cells)
    duplicate_penalty = min(duplicate_rows * 0.05, 0.25)
    conversion_penalty = min(sum(conversion_issues.values()) * 0.03, 0.20)
    quality_score = round(max(0, min(100, (mapping_score * 45 + completeness_score * 55) * 100 / 100 - (duplicate_penalty + conversion_penalty) * 100)), 1)

    unmapped = [item["Source Column"] for item in diagnostics if not item["Mapped Column"]]
    report = {
        "quality_score": quality_score,
        "source_columns": list(map(str, source_df.columns)),
        "mapped_columns": {str(k): v for k, v in mapping.items()},
        "mapping_diagnostics": diagnostics,
        "unmapped_columns": unmapped,
        "duplicate_supplier_rows": duplicate_rows,
        "duplicate_suppliers": duplicate_suppliers,
        "missing_cells": missing_cells,
        "numeric_conversion_issues": conversion_issues,
        "row_count": int(len(normalized)),
        "column_count": int(len(normalized.columns)),
    }
    normalized.attrs["rfq_quality_report"] = report
    return normalized, report


def quality_report_messages(report):
    """Translate RFQ quality diagnostics into user-facing messages."""
    messages = []
    if report["unmapped_columns"]:
        messages.append("Unmapped columns preserved: " + ", ".join(report["unmapped_columns"]))
    if report["duplicate_supplier_rows"]:
        messages.append("Duplicate supplier rows detected: " + ", ".join(report["duplicate_suppliers"]))
    if report["numeric_conversion_issues"]:
        detail = ", ".join(f"{key} ({value})" for key, value in report["numeric_conversion_issues"].items())
        messages.append("Non-numeric values converted to blank: " + detail)
    messages.append(f"RFQ upload quality score: {report['quality_score']}/100")
    return messages
