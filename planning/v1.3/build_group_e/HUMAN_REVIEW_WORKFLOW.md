# Build Group E Human Review Workflow

## States

`ROUTE_DISABLED`, `NO_FILE`, `FILE_RECEIVED`, `ADAPTER_FATAL`, `MAPPING_CONFIRMATION_REQUIRED`, `EVENT_SELECTION_REQUIRED`, `ADAPTER_READY`, `ORCHESTRATION_BLOCKED`, `INSUFFICIENT_EVIDENCE`, `CONDITIONAL_REVIEW_REQUIRED`, `ANALYTICAL_REVIEW_READY`, `ITEM_SELECTION_REQUIRED`, `ANALYSIS_INCOMPATIBLE`, and `REVIEW_ONLY_COMPLETE`.

`READY_FOR_HANDOFF` and `HANDOFF_CONFIRMED` remain reserved states but are unreachable for governed workbooks in Build Group E.

## Workflow

1. Upload one governed XLSX workbook.
2. Clear prior review state when the upload SHA-256 changes.
3. Confirm high-risk normalized header mappings.
4. Select one sourcing event when multiple events exist.
5. Run Build D in the workbook comparison currency.
6. Review blockers, warnings, evidence, source values, normalized values and provenance.
7. Select one RFQ item.
8. Acknowledge only warnings classified as acknowledgement-required.
9. End in `REVIEW_ONLY_COMPLETE` with no analytical DataFrame.

## Governance

`BLOCKED` and `INSUFFICIENT_EVIDENCE` never proceed. Unknown warnings fail closed. Ignored original columns remain provenance-only. `GOVERNED_RANKING_INPUTS_NOT_CANONICAL` explains why future canonical Build B/C work is required before analytical handoff.
