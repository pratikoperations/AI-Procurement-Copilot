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
  -> row validity, composite-key, quotation-version and event-selection controls
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
- active quotation-version status;
- explicit `valid_for_analysis` status.

## Mapping behaviour

1. Exact canonical headers are accepted for the governed template.
2. Approved SAP aliases are applied through `sap_report_alias_registry_v1.3.0.json`.
3. Punctuation/spacing-normalized aliases are visible as `NORMALIZED_APPROVED`.
4. High-risk normalized mappings require an explicit `(sheet, source_header, canonical_field)` confirmation.
5. Ambiguous or duplicate canonical targets are Fatal.
6. Unmapped columns remain visible as Information findings and are excluded from calculations.

No fuzzy matching implementation is included.

## Row validity and eligibility

Rows remain in the adapter result for audit even when they are unusable. A row is marked `valid_for_analysis = false` when it carries a row-level Fatal or Blocking finding, including:

- formula rejection in governed fields;
- missing mandatory values;
- invalid typed values;
- non-positive quantity or price-unit values;
- negative governed prices;
- invalid row currency format.

Sheet-level mapping failures also invalidate affected sheet rows:

- ambiguous header mapping;
- duplicate canonical target;
- missing mandatory header;
- unconfirmed normalized high-risk mapping.

Only records that are both `active` and `valid_for_analysis` can support valid-record totals or the minimum-supplier gate. Blocked, Fatal and superseded records remain visible but contribute no eligibility evidence.

## Validation behaviour

- Fatal: missing or empty RFQ sheet, missing header/value, unsafe type conversion, contradictory duplicate key, unsupported schema version, multiple metadata rows, invalid event selection or no valid quotation records.
- Blocking: high-risk mapping confirmation, formula in governed fields, non-positive quantities/price units, negative governed prices, invalid hash/currency/anonymization metadata, unresolved latest-version conflict, insufficient valid supplier count or missing event selection.
- Warning: duplicate business payloads, optional formula cells and missing PO history in Full Review mode.
- Information: unknown sheets and unmapped source columns.

## Metadata contract enforcement

When `UPLOAD_METADATA` is present:

- no more than one non-empty metadata row is permitted;
- `SCHEMA_VERSION` must equal `1.3.0`;
- `UPLOAD_MODE` must be an approved mode;
- `SOURCE_FILE_HASH_SHA256` must be 64 hexadecimal characters;
- `ANONYMIZATION_STATUS` must be an approved value;
- `BASE_CURRENCY` must be a three-letter uppercase code.

The metadata sheet remains optional for portfolio-mode inference, as defined by the Build Group B contract.

## Composite keys and duplicate equivalence

RFQ duplicate identity uses:

```text
SOURCING_EVENT_ID + RFQ_NUMBER + RFQ_ITEM + SUPPLIER_ID + QUOTATION_VERSION
```

PO-history duplicate identity uses:

```text
PO_NUMBER + PO_ITEM
```

Duplicate comparison excludes provenance-only fields:

- `SOURCE_ROW_ID`;
- `SOURCE_FILE_NAME`;
- `SOURCE_EXTRACTED_AT`.

The same business payload under the same key is a Warning. A conflicting business payload under the same key is Fatal.

## Quotation versions

All versions are retained. The unique highest integer version is marked active for each event/RFQ/item/supplier group. Ambiguous highest versions are Blocking. Superseded versions never count as additional valid suppliers.

## Event selection

A workbook may contain multiple sourcing events, but exactly one event must be selected before downstream analysis. Build Group C filters returned RFQ records only after validating that the selected event exists. If the selected event has no valid active quotations, the adapter returns a Fatal finding.

## Supplier-count eligibility

The minimum-supplier gate counts unique suppliers only from quotation records that are:

- within the selected event when selection applies;
- the active quotation version;
- `valid_for_analysis`;
- commercially identifiable through the canonical RFQ item and supplier fields.

Two uploaded supplier rows do not satisfy the gate when one row is blocked or Fatal. Three uploaded supplier rows may satisfy the gate when one is blocked and two remain valid.

## Formula policy

Workbooks are opened with `data_only=False`. Formula cells are detected from cell type and cached values are not used. Governed commercial/key formulas are Blocking; optional descriptive formulas are Warning. When formula or other validation findings leave no valid active quotation records, the workbook or selected event receives a Fatal no-valid-record finding.

## Hash policy

- `SOURCE_FILE_HASH_SHA256` is read from workbook metadata and validated when metadata is supplied.
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
