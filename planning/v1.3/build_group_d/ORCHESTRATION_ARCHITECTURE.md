# AI Procurement Copilot v1.3 — Build Group D Orchestration Architecture

## Boundary

`AdapterResult` → evaluation context → conditional rules → source-preserving currency/UOM normalization → evidence coverage → analysis-only eligibility.

The layer does not import or invoke Streamlit, scoring, TCO, recommendation, persistence, SAP APIs, or deployment code.

## Evaluation date

Precedence: explicit caller date, `UPLOAD_CREATED_AT`, `EXTRACTED_AT`, latest valid `SOURCE_EXTRACTED_AT`, then system date with `SYSTEM_DATE_FALLBACK` warning.

## Normalization

- No silent USD default.
- Same currency/UOM use factor 1.
- FX is source-currency units per one comparison-currency unit; normalized price divides by FX.
- UOM factor is comparison units per source unit; quantity multiplies and unit price divides.
- Original canonical values remain unchanged; normalized values and provenance are separate.

## Conditional rules

Material identity, UOM conversion, FX, Full Review history metadata/window, quotation expiry, and 60-day history staleness are enforced without inventing business evidence.

## Evidence and eligibility

Policy `AIPC-EVIDENCE-COVERAGE-1.3.0` uses eight dimensions and a 70% gate. Per-item coverage uses the minimum valid supplier coverage. Event coverage is requested-quantity weighted, otherwise equal-item weighted with disclosure.

Statuses are limited to `BLOCKED`, `INSUFFICIENT_EVIDENCE`, `ELIGIBLE_WITH_CONDITIONS`, and `ELIGIBLE_FOR_ANALYSIS`. No award or recommendation claim is produced.
