# Build Group E Acceptance Criteria

## Scope

Only the authorized 15 files may change. Build B/C, Build D and all procurement engines remain unchanged.

## Route isolation

- Governed data bypasses legacy fuzzy mapping and legacy currency normalization.
- Legacy and synthetic routes bypass Build C and Build D.
- Governed data always returns no analytical DataFrame.
- Governed processing stops before validation, scoring, TCO, recommendation, allocation and negotiation.
- Governed failures cannot fall through to another route.

## Review governance

- Build D outcomes map to distinct states.
- `BLOCKED` and `INSUFFICIENT_EVIDENCE` cannot proceed.
- Warning policy version is `AIPC-COMPATIBILITY-WARNING-DISPOSITION-1.3.0`.
- Unknown warnings are compatibility blocking.
- Mapping, event and RFQ-item choices are explicit.
- Final governed state is `REVIEW_ONLY_COMPLETE`.

## Canonical-schema boundary

- `GOVERNED_RANKING_INPUTS_NOT_CANONICAL` is always present in compatibility review.
- `CanonicalRecord.original_values` and ignored columns are provenance-only.
- Malformed or populated ignored ranking columns never enter calculations or a DataFrame.
- Future analytical handoff requires a separately authorized canonical Build B/C schema extension.

## Currency

- Source currencies may include USD, INR and other governed currencies.
- Workbook `BASE_CURRENCY` remains the Build D review comparison currency.
- Source price, source currency, FX rate/date, normalized review value and row provenance remain visible.
- INR comparison values are never labelled USD.
- USD, INR and Both remain review/display modes only.
- Governed data is never normalized a second time.

## Session reset

- A workbook SHA-256 is calculated before adapter replay uses prior selections.
- A changed hash clears mapping, event, item, warning and former handoff state.
- Same-file reruns preserve current review choices.

## Validation

- A generated XLSX fixture covers Build C, Build D and Build E with multiple events, item selection, mixed USD/INR quotations, governed FX evidence, mapping confirmation, warning acknowledgement and review-only completion.
- Adversarial tests prove ignored columns remain provenance-only, INR is not falsely labelled USD, prior workbook decisions do not transfer, and governed processing cannot reach scoring.
- Full repository tests and Streamlit smoke test pass.

## Claims and rollback

- Global v1.2 label remains.
- New route is a governed v1.3 workbook-review preview.
- Environment flag is disabled by default and malformed values fail closed.
- No deployment, persistence, SAP write-back, tag or release changes.
