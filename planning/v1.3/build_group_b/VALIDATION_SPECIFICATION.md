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

Evidence policy ID: `AIPC-EVIDENCE-COVERAGE-1.3.0`.

Coverage is calculated per active supplier quotation per RFQ item. Only valid, active quotations enter item recommendation gating. Blocked quotations remain visible but contribute no recommendation evidence. Event coverage is the requested-quantity-weighted aggregation of evaluated RFQ-item coverage; if requested quantities are not comparable, use an equal-item average and disclose that fallback.

| Dimension | Minimum approved evidence | Weight |
|---|---|---:|
| Comparable price basis | valid base price, positive price unit, currency, comparison UOM, and required FX/UOM conversions | 25% |
| Quantity and availability | requested quantity, quoted quantity, and full-quantity availability or an approved quantity-coverage rule | 15% |
| Commercial terms | at least one approved payment-term or Incoterms evidence set | 10% |
| Delivery | lead time or promised delivery date | 10% |
| Quality | approved quality score or governed quality evidence | 10% |
| Risk | approved risk score or governed risk evidence | 10% |
| ESG | approved ESG score or governed ESG evidence | 5% |
| Historical benchmark | approved non-stale historical match with disclosed match level | 15% |

Rules:

- Non-applicable dimensions are removed from the denominator only through an approved, versioned policy.
- Missing applicable dimensions receive zero coverage for that dimension.
- Partial evidence does not receive partial credit unless a future approved policy defines it.
- Coverage at or above 70% permits conditional best-value language, subject to all Blocking rules.
- Coverage below 70% permits analysis but withholds final recommendation language.
- Omitted dimensions, denominator changes, adjusted scoring weights and aggregation method must be disclosed.

## Formula-cell controls

- Formula cells in identity, quantity, price, currency, UOM, date, status, FX and key fields are Blocking or Fatal depending on whether valid quotation records remain.
- Formula cells in optional descriptive fields are Warning findings.
- Cached formula values must not be silently accepted as source evidence.

## Additional governed defaults

- Expired quotations remain visible as blocked evidence and are excluded from active comparison.
- Tax is excluded from comparable TCO unless an approved policy classifies it as non-recoverable and comparable.
- Historical evidence older than 60 days creates a default staleness Warning unless an approved policy overrides it.

## Null handling

No optional blank may be coerced to zero for TCO or scoring. Incomplete TCO must be labelled incomplete. Missing scoring dimensions are excluded and remaining weights are renormalized only under an approved scoring policy.
