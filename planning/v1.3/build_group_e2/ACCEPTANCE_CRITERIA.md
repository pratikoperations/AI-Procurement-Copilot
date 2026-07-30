# Build Group E2 — Acceptance Criteria

- Only schema v1.3.1 `FULL_SOURCING_REVIEW` may become analytically eligible.
- Quick RFQ and v1.3.0 remain review-only.
- At least two selected eligible suppliers are required.
- Quotation, ranking-eligibility and handoff DataFrame supplier sets are identical.
- Every supplier has ten `VALID` canonical ranking fields and one direct eligible `MATCHED` ranking scope without fallback.
- Required commercial inputs are present, valid and canonical: normalized USD price, MOQ, lead time, payment terms and Incoterms.
- The analytical basis is USD and one comparison UOM applies.
- No analytical value comes from original, ignored, unmapped, source-status or defaulted data.
- Before confirmation the state is `READY_FOR_HANDOFF` and no DataFrame is returned.
- Exact current digest confirmation is required for `HANDOFF_CONFIRMED`.
- Upload, selection, mapping, evidence, assumptions, commercial values or contract changes invalidate confirmation.
- Input validation precedes scoring; scored-output validation precedes recommendations; any failure blocks later stages.
- Disabling the E2 feature flag restores review-only operation.
- No B2, C2, Build D or frozen analytical-engine file is modified.
