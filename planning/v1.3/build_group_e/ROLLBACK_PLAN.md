# Build Group E Rollback Plan

## Runtime disablement

`AIPC_GOVERNED_V13_ROUTE_ENABLED` is disabled by default. Enabled values are `1`, `true`, `yes`, and `on`. Missing, disabled or malformed values prevent Build C and Build D invocation while preserving demo and legacy routes. No hosted environment setting is changed by this PR.

## Review-only isolation

Governed workbooks never produce an analytical DataFrame and therefore cannot reach validation, scoring, TCO, recommendation, allocation or negotiation. Governed processing bypasses legacy fuzzy mapping and currency normalization and cannot fall through to synthetic or legacy data.

## Upload reset

The controller stores the current workbook SHA-256. A changed hash clears mapping confirmations, event selection, RFQ-item selection, warning acknowledgements and former handoff state before those values are used. Same-file reruns retain current review state.

## Code rollback

The Build Group E PR modifies only `app.py` and `modules/sidebar.py`; all other files are additive. The merge remains independently revertible. No database, schema migration, persistence, deployment change or external integration is introduced.

## Future enablement

Analytical handoff remains blocked by `GOVERNED_RANKING_INPUTS_NOT_CANONICAL`. Removing that blocker requires a separately reviewed canonical Build B/C schema extension and is not part of rollback or runtime configuration.
