# Build Group C2 — Acceptance Criteria

- v1.3.0 workbooks retain frozen three-sheet behavior.
- v1.3.1 is selected only from `UPLOAD_METADATA.SCEMA_VERSION`/`SCHEMA_VERSION`; fourth-sheet presence never silently upgrades a workbook.
- The frozen v1.3.0 schema resolves locally through the B2 URN without network access.
- `SUPPLIER_RANKING_INPUTS` is parsed only for v1.3.1.
- Every non-canonical ranking alias requires a confirmation bound to upload hash, schema version, registry version, header, field, scale, and origin.
- Per-field `VALUE_ORIGINS` are retained; engine defaults are prohibited.
- `SOURCE_EVIDENCE_STATUS` remains optional and non-authoritative.
- Canonical evidence status is derived independently for each field using the frozen precedence.
- Freshness, evidence, duplicates, contradictions, overlaps, and version conflicts generate deterministic findings.
- Scope matching follows plant-material-group, material-group, purchasing-org, supplier-global precedence.
- Quick RFQ and Full Review eligibility is calculated per RFQ item and supplier.
- Build D inputs remain unchanged.
- Build E remains review-only with no DataFrame, no handoff, and the canonical-ranking blocker retained.
- All generated XLSX, adversarial, regression, and Streamlit smoke tests pass.
