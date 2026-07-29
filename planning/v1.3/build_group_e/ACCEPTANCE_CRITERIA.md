# Build Group E Acceptance Criteria

## Scope

Only the authorized 15 files may change. Build C, Build D and all procurement engines remain unchanged.

## Route isolation

- Governed data bypasses legacy fuzzy mapping and legacy currency normalization.
- Legacy and synthetic routes bypass Build C and Build D.
- A governed stop state cannot fall through to another route.
- Scoring is unreachable before `HANDOFF_CONFIRMED`.

## Review governance

- Build D outcomes map to distinct states.
- `BLOCKED` and `INSUFFICIENT_EVIDENCE` cannot proceed.
- Warning policy version is `AIPC-COMPATIBILITY-WARNING-DISPOSITION-1.3.0`.
- Unknown warnings are compatibility blocking.
- Mapping, event and RFQ-item choices are explicit.
- Composite identity changes invalidate handoff.

## Compatibility

- Manifest version is `AIPC-LEGACY-COMPATIBILITY-MANIFEST-1.3.0`.
- Exactly one event and RFQ item, one comparison UOM and at least two eligible suppliers.
- Supplier name, positive canonical USD price, positive MOQ, non-negative lead time, payment terms and Incoterms are mandatory.
- Ranking-sensitive existing-engine inputs may not be silently defaulted.

## Currency

- Source currencies may include USD, INR and governed foreign currencies.
- Source price, currency, FX rate/date and normalized value remain visible.
- Existing engines receive canonical USD only.
- Display modes support USD, INR and Both.
- Both is one result with two presentations.
- Governed data is not normalized a second time.
- No non-USD value may be labelled USD.

## Claims and rollback

- Global v1.2 label remains.
- New route is a governed v1.3 workbook-review preview.
- Environment flag is disabled by default and malformed values fail closed.
- No deployment, persistence, SAP write-back, tag or release changes.

## Validation

Focused state, controller, compatibility, currency, UI-contract and app-route tests pass; full repository tests and Streamlit smoke test pass.
