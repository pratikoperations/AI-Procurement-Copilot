# AI Procurement Copilot v1.3 — Validation Specification

## Severity model

### Fatal

Rejects the workbook or sourcing event before analysis.

- `RFQ_QUOTES` missing.
- File encrypted, corrupt, renamed, unsafe, or unsupported.
- Mandatory headers absent.
- Unsupported schema version.
- Contradictory duplicate primary keys.
- Required numeric fields are not parseable.
- No valid quotation records remain.

### Blocking

Excludes a row/event from recommendation or withholds recommendation language.

- Fewer than two valid suppliers for the evaluated RFQ item.
- Requested or quoted quantity is zero or negative.
- Base price is negative.
- Price unit is zero or negative.
- Quotation is expired at the approved evaluation date.
- Mixed currency without an approved exchange rate and date.
- Different UOM without an approved conversion factor.
- Unresolved quotation-version conflict.
- Missing supplier, RFQ, item, or sourcing-event identity.
- Explicit failed technical approval.
- Rejected, withdrawn, or invalid quotation.

### Warning

Analysis may continue with a disclosed limitation.

- `PO_HISTORY` absent.
- No exact historical match.
- Freight, payment terms, Incoterms, lead time, delivery date, supplier performance, quality, risk, or ESG evidence unavailable.
- History is stale.
- Benchmark is category-level rather than material-level.
- Quote validity expires soon.
- `UPLOAD_METADATA` absent in portfolio mode.

### Information

Audit-only or explanatory finding with no direct calculation effect.

## Aggregation

- Any Fatal finding rejects the workbook/event.
- Blocking findings prevent affected rows from supporting final recommendation language.
- Warnings disable only the affected capability.
- Information findings remain visible in the audit record.

## Mapping controls

High-risk identity and commercial fields must never be accepted solely through low-confidence fuzzy matching:

- sourcing event;
- RFQ number and item;
- supplier ID;
- quotation version;
- quantity;
- price;
- price unit;
- currency;
- UOM;
- exchange rate.

Unresolved mappings require explicit user confirmation or correction.

## Evidence coverage

Evidence coverage is calculated over approved applicable dimensions, not raw cell completeness.

Initial governed dimension groups:

1. comparable price basis;
2. quantity and availability;
3. commercial terms;
4. delivery evidence;
5. quality evidence;
6. risk evidence;
7. ESG evidence;
8. historical benchmark evidence.

Only applicable dimensions enter the denominator. A dimension is covered only when its minimum approved fields pass validation.

- Coverage at or above 70% permits conditional best-value language, subject to all blocking rules.
- Coverage below 70% permits analysis but withholds final recommendation language.
- Omitted dimensions and adjusted weights must be disclosed.

## Null handling

No optional blank may be coerced to zero for TCO or scoring. Incomplete TCO must be labelled incomplete. Missing scoring dimensions are excluded and remaining weights are renormalized only under an approved scoring policy.
