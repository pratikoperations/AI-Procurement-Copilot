# Build Group E2 — Controlled Analytical Handoff Contract

## Boundary

E2 bridges governed v1.3.1 Full Sourcing Review evidence to the frozen analytical engines. Quick RFQ and every v1.3.0 workbook remain review-only.

## Eligibility

Analytical handoff requires the default-off E2 feature flag, a selected eligible RFQ item, at least two suppliers, exact quotation/ranking/DataFrame supplier-set equality, ten VALID C2 ranking fields per supplier, one direct MATCHED scope per supplier, complete commercial inputs, one comparison UOM and USD analytical currency.

## Prohibited sources

`CanonicalRecord.original_values`, ignored or unmapped columns, `SOURCE_EVIDENCE_STATUS`, legacy defaults and non-valid canonical evidence are never analytical inputs.

## Confirmation

Machine-ready workbooks stop at `READY_FOR_HANDOFF` with no DataFrame. The user must confirm the current deterministic SHA-256 digest. Any governed identity, supplier, evidence, commercial input, assumption or contract-version change invalidates confirmation.

## Confirmed result

Only exact confirmation returns `HANDOFF_CONFIRMED`, a governed DataFrame, `analysis_handoff_allowed=True` and `handoff_confirmed=True`.

## Currency

Scoring and TCO are USD-based. INR and Both are display-only transformations.

## Rollback

Disabling `AIPC_GOVERNED_V13_ANALYTICAL_HANDOFF_ENABLED` restores the pre-E2 review-only route without changing B2, C2 or Build D.
