# AI Procurement Copilot v1.3 — Minimum SAP Workbook Contract

## Status

- Contract ID: `AIPC-SAP-MINIMUM-INTAKE`
- Contract version: `1.3.0`
- Release target: AI Procurement Copilot v1.3 — SAP Minimum Intake and Single-User Operational Foundation
- Status: Draft contract foundation
- Scope: file-based, read-only intake
- Not a live SAP integration, API connection, ERP write-back, autonomous award system, or production deployment.

## Workbook identity

Canonical filename:

`PROCUREMENT_COPILOT_UPLOAD.xlsx`

Approved sheets:

1. `RFQ_QUOTES` — mandatory.
2. `PO_HISTORY` — optional.
3. `UPLOAD_METADATA` — optional in portfolio mode and required for governed internal use.

Unknown sheets may be logged but must not be interpreted without an approved future contract extension.

## Supported modes

### QUICK_RFQ

- Requires `RFQ_QUOTES`.
- Performs current-event quotation validation and comparison.
- Does not make historical-price or supplier-history claims when `PO_HISTORY` is absent.

### FULL_SOURCING_REVIEW

- Requires `RFQ_QUOTES`.
- Uses `PO_HISTORY` when present and valid.
- Supports governed historical benchmarking with disclosed matching confidence.

### SYNTHETIC_DEMO

- Requires no user upload.
- Uses version-controlled synthetic assets.
- Must display an explicit Synthetic Demo label.
- Must never be presented as production or realized-savings evidence.

## Canonical grains and keys

### RFQ_QUOTES

Grain: one supplier quotation for one RFQ item and quotation version.

Composite key:

`SOURCING_EVENT_ID + RFQ_NUMBER + RFQ_ITEM + SUPPLIER_ID + QUOTATION_VERSION`

### PO_HISTORY

Grain: one historical PO item.

Key:

`PO_NUMBER + PO_ITEM`

### UPLOAD_METADATA

Grain: one upload metadata record for the workbook.

## Null semantics

Blank optional commercial or evaluation values are unknown.

- Missing freight is not zero freight.
- Missing payment terms do not imply immediate or standard payment terms.
- Missing scores are excluded from approved scoring dimensions.
- Missing historical data disables historical claims.
- Missing optional data must not be replaced with favourable assumptions.

## Original and normalized values

The intake layer must preserve original source values and create separate governed normalized values. It must retain transformation provenance including source file, source row, mapping version, conversion factor and analysis version.

## Compatibility rule

This contract is additive. It does not replace or alter the frozen v1.1 seven-sheet ERP preview or the legacy flat RFQ upload. Legacy removal requires separate authorization after deterministic parity is demonstrated.

## Hash semantics

- `SOURCE_FILE_HASH_SHA256` identifies the original SAP/Fiori/company export before canonical preparation and may be recorded in `UPLOAD_METADATA`.
- `UPLOAD_FILE_HASH_SHA256` identifies the completed canonical workbook presented to the application. It is calculated during ingestion and stored in the external event/audit record, not inside the workbook being hashed.
- This separation prevents self-referential workbook hashing.

## Controlled analysis rules

- A workbook may contain more than one `SOURCING_EVENT_ID`, but the user must explicitly select exactly one event before analysis. Cross-event aggregation is prohibited.
- Expired quotations remain visible as blocked evidence and are excluded from active comparison and recommendation calculations.
- Tax is excluded from comparable TCO unless an approved policy identifies it as non-recoverable and comparable.
- Historical data older than 60 days produces a default staleness warning unless an approved policy overrides the threshold.
