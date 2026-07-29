# AI Procurement Copilot v1.3 — Build Group C Adapter Architecture

## Status

- Build group: C — RFQ Workbook Adapter
- Scope: isolated intake, mapping, typed parsing, provenance and adapter-level validation
- Runtime integration: not authorized
- Procurement engines: unchanged
- Persistence: not implemented
- Live SAP connectivity or write-back: not implemented

## Boundary

```text
v1.3 XLSX workbook
  -> existing erp_workbook_loader package-safety checks
  -> canonical/alias header mapping
  -> explicit mapping-review evidence
  -> typed RFQ_QUOTES / PO_HISTORY / UPLOAD_METADATA records
  -> composite-key, quotation-version and event-selection controls
  -> adapter findings and provenance
  -X-> procurement engines until a later controlled integration build
```

## Authoritative implementation

- `modules/rfq_workbook_adapter.py`
- `tests/test_rfq_workbook_adapter.py`

The adapter imports and reuses `modules.erp_workbook_loader.load_erp_workbook` before reading rows. Existing extension, size, ZIP package, macro, external-link, connection, query-table and external-data controls therefore remain authoritative.

## Result model

`AdapterResult` returns:

- detected upload mode;
- schema and alias-registry versions;
- external upload-file SHA-256;
- source-export SHA-256 when supplied by metadata;
- available and selected sourcing events;
- typed RFQ quotation records;
- typed PO history records;
- upload metadata;
- mapping-review records;
- adapter-level findings.

Each canonical record contains:

- original source-header/value mapping;
- typed canonical values;
- a separate normalized-values mapping, intentionally empty in Build Group C;
- immutable row provenance;
- active quotation-version status.

## Mapping behaviour

1. Exact canonical headers are accepted for the governed template.
2. Approved SAP aliases are applied through `sap_report_alias_registry_v1.3.0.json`.
3. Punctuation/spacing-normalized aliases are visible as `NORMALIZED_APPROVED`.
4. High-risk normalized mappings require an explicit `(sheet, source_header, canonical_field)` confirmation.
5. Ambiguous or duplicate canonical targets are Fatal.
6. Unmapped columns remain visible as Information findings and are excluded from calculations.

No fuzzy matching implementation is included.

## Validation behaviour

- Fatal: missing RFQ sheet/header/value, unsafe type conversion, contradictory duplicate key, invalid event selection or upload mode.
- Blocking: high-risk mapping confirmation, formula in governed fields, non-positive quantities/price units, negative governed prices, unresolved latest-version conflict, insufficient supplier count or missing event selection.
- Warning: exact duplicate rows, optional formula cells and missing PO history in Full Review mode.
- Information: unknown sheets and unmapped source columns.

## Quotation versions

All versions are retained. The unique highest integer version is marked active for each event/RFQ/item/supplier group. Ambiguous highest versions are Blocking.

## Event selection

A workbook may contain multiple sourcing events, but exactly one event must be selected before downstream analysis. Build Group C filters returned RFQ records only after validating that the selected event exists.

## Formula policy

Workbooks are opened with `data_only=False`. Formula cells are detected from cell type and their cached values are not used. Governed commercial/key formulas are Blocking; optional descriptive formulas are Warning.

## Hash policy

- `SOURCE_FILE_HASH_SHA256` is read from workbook metadata when supplied.
- `UPLOAD_FILE_HASH_SHA256` is calculated from the exact uploaded bytes and returned externally in `AdapterResult` and row provenance.
- The adapter does not write a self-referential upload hash into the workbook.

## Explicit exclusions

- no application routing or Streamlit controls;
- no procurement-engine invocation;
- no currency or UOM normalization implementation;
- no TCO or scoring changes;
- no persistence or audit database;
- no SAP API or write-back;
- no deployment changes.
