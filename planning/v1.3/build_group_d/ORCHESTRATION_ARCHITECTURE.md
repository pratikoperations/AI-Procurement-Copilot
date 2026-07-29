# AI Procurement Copilot v1.3 — Build Group D Orchestration Architecture

## Boundary

`AdapterResult` → evaluation context → conditional rules → source-preserving currency/UOM normalization → deterministic history matching → evidence coverage → analysis-only eligibility.

The layer does not import or invoke Streamlit, scoring, TCO, recommendation, persistence, SAP APIs, or deployment code.

## Evaluation date

Precedence: explicit caller date, `UPLOAD_CREATED_AT`, `EXTRACTED_AT`, latest valid `SOURCE_EXTRACTED_AT`, then system date with `SYSTEM_DATE_FALLBACK` warning.

## Normalization

- No silent USD default.
- Source quantity must be positive.
- Source price must be non-negative.
- `PRICE_UNIT` must be positive.
- Same currency/UOM use factor 1.
- FX is source-currency units per one comparison-currency unit; normalized price divides by FX.
- UOM factor is comparison units per source unit; quantity multiplies and unit price divides.
- Original canonical values remain unchanged; normalized values and provenance are separate.
- Tax remains excluded. No public tax-composition parameter exists in Build Group D.

## Conditional rules

Material identity, UOM conversion, FX, Full Review history metadata/window, quotation expiry, and history staleness are governed without inventing business evidence.

History staleness is calculated independently for every structurally valid, normalized, in-window history row. Rows older than 60 days remain visible but are ineligible for benchmark matching. Current rows remain eligible even when stale rows are present.

Excluded, stale, optional, or out-of-window history normalization defects remain visible at row level and do not automatically block current RFQ analysis. Applicable invalid Full Review history disables historical evidence and emits `HISTORY_NORMALIZATION_INVALID`.

## Deterministic historical matching

The hierarchy is:

1. unique exact `MATERIAL_ID`;
2. unique exact `MATERIAL_GROUP` plus deterministic normalized description;
3. approved quote-row to history-row mapping;
4. explicit manual quote-row/history-row confirmation.

Approved mappings and manual confirmations may resolve ambiguous automatic candidates. Unresolved ambiguity emits `HISTORICAL_MATCH_AMBIGUOUS`, records candidate history row IDs and receives zero historical credit. No fuzzy automatic matching is permitted.

## Evidence and eligibility

Policy `AIPC-EVIDENCE-COVERAGE-1.3.0` uses eight dimensions and a 70% gate.

- Comparable-price evidence requires normalized unit price greater than zero.
- Zero price remains structurally permitted but emits `ZERO_PRICE_REQUIRES_CLASSIFICATION` and receives no comparable-price credit.
- `TECHNICALLY_APPROVED=False` does not earn quality credit.
- Quality, risk and ESG scores receive credit only when numeric and within 0–100.
- Commercial charges must be non-zero to count as evidence; governed text terms may count when non-blank.
- Event weighting uses one unique positive requested quantity per RFQ item.
- Conflicting requested quantities produce `RFQ_ITEM_REQUESTED_QUANTITY_CONFLICT` and block analysis.
- Invalid or missing quantities never enter the weighted denominator.
- Per-item coverage uses minimum valid supplier coverage.
- Event coverage is requested-quantity weighted; equal-item fallback is explicitly disclosed when permitted.

Statuses are limited to `BLOCKED`, `INSUFFICIENT_EVIDENCE`, `ELIGIBLE_WITH_CONDITIONS`, and `ELIGIBLE_FOR_ANALYSIS`. No award or recommendation claim is produced.
