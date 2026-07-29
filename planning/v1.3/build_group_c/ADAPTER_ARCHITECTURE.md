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
  -> row-validity assessment
  -> latest-valid quotation-version selection
  -> sourcing-event eligibility
  -> adapter findings and provenance
  -X-> procurement engines until a later controlled integration build
```

## Authoritative implementation

- `modules/rfq_workbook_adapter.py`
- `tests/test_rfq_workbook_adapter.py`

The adapter reuses `modules.erp_workbook_loader.load_erp_workbook` before reading rows. Existing extension, size, ZIP package, macro, external-link, connection, query-table and external-data controls remain authoritative.

## Result model

`AdapterResult` returns:

- detected upload mode;
- schema and alias-registry versions;
- external upload-file SHA-256;
- source-export SHA-256 when supplied by metadata;
- available and selected sourcing events;
- typed RFQ quotation records;
- typed PO-history records;
- upload metadata;
- mapping-review records;
- adapter-level findings.

Each canonical record contains:

- original source-header/value mapping;
- typed canonical values;
- a separate normalized-values mapping, intentionally empty in Build Group C;
- immutable row provenance;
- active quotation-version status;
- `row_valid`, representing structural and row-level validity;
- `eligible_for_analysis`, representing whether the record may support valid counts or later recommendation workflows.

`valid_for_analysis` remains a backward-compatible property that returns `eligible_for_analysis`.

## Mapping behaviour

1. Exact canonical headers are accepted for the governed template.
2. Approved SAP aliases are applied through `sap_report_alias_registry_v1.3.0.json`.
3. Punctuation/spacing-normalized aliases are visible as `NORMALIZED_APPROVED`.
4. High-risk normalized mappings require an explicit `(sheet, source_header, canonical_field)` confirmation.
5. Ambiguous or duplicate canonical targets are Fatal.
6. Unmapped columns remain visible as Information findings and are excluded from calculations.

No fuzzy matching implementation is included.

## Row validity

A row is structurally valid only when it has no row-level Fatal or Blocking finding and no applicable sheet-level mapping blocker.

Row-level blockers include:

- formulas in governed fields;
- invalid or missing mandatory values;
- invalid types;
- non-positive governed quantities or price units;
- negative governed commercial values;
- invalid currency format.

Rows remain visible for audit even when `row_valid` is false.

## Latest-valid quotation-version selection

Quotation versions are grouped by:

```text
SOURCING_EVENT_ID
+ RFQ_NUMBER
+ RFQ_ITEM
+ SUPPLIER_ID
```

The adapter applies row validity before selecting an active version.

- The unique highest valid integer version becomes active.
- A later invalid version remains visible but inactive.
- A valid earlier version remains active when a later version is blocked.
- If every version is invalid, the supplier contributes no active valid quotation.
- If the highest valid version is duplicated or otherwise ambiguous, the entire quotation group is ineligible and emits `QUOTATION_VERSION_CONFLICT`.

Superseded and invalid versions never add supplier-count eligibility.

## Event eligibility

Structural row validity and event eligibility are separate controls.

- A single-event workbook may proceed without an explicit selection.
- A multi-event workbook with no selection emits `SOURCING_EVENT_SELECTION_REQUIRED`.
- While that finding is active, all quotation records remain structurally auditable but `eligible_for_analysis` is false.
- After a valid event is selected, only records for that event are returned and eligible active records may support valid counts.
- An invalid selection is Fatal.

## Supplier-count eligibility

The minimum-supplier gate counts only records that are:

- structurally valid;
- analysis eligible;
- the active latest-valid quotation version;
- within the selected sourcing event when selection is required;
- associated with a non-null supplier identity.

Blocked, conflicted, invalid and superseded records do not satisfy the supplier threshold.

## Validation behaviour

- Fatal: missing RFQ sheet/header/value, unsafe type conversion, contradictory duplicate key, invalid event selection or upload mode, empty RFQ data, or no valid quotation records.
- Blocking: high-risk mapping confirmation, formula in governed fields, non-positive quantities/price units, negative governed prices, unresolved latest-valid version conflict, insufficient valid supplier count, or missing event selection.
- Warning: duplicate business payload, optional formula cells and missing PO history in Full Review mode.
- Information: unknown sheets and unmapped source columns.

## Formula policy

Workbooks are opened with `data_only=False`. Formula cells are detected from cell type and cached values are not used. Governed commercial/key formulas are Blocking; optional descriptive formulas are Warning.

## Hash policy

- `SOURCE_FILE_HASH_SHA256` is read from workbook metadata when supplied and validated as 64 hexadecimal characters.
- `UPLOAD_FILE_HASH_SHA256` is calculated from the exact uploaded bytes and returned externally in `AdapterResult` and row provenance.
- The adapter does not write a self-referential upload hash into the workbook.

## Explicit exclusions

- no application routing or Streamlit controls;
- no procurement-engine invocation;
- no currency or UOM normalization implementation;
- no TCO or scoring changes;
- no persistence or audit database;
- no SAP API or write-back;
- no deployment changes;
- no Build Group D implementation.
