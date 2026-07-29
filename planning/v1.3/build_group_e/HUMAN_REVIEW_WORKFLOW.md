# Build Group E Human Review Workflow

## States

`ROUTE_DISABLED`, `NO_FILE`, `FILE_RECEIVED`, `ADAPTER_FATAL`, `MAPPING_CONFIRMATION_REQUIRED`, `EVENT_SELECTION_REQUIRED`, `ADAPTER_READY`, `ORCHESTRATION_BLOCKED`, `INSUFFICIENT_EVIDENCE`, `CONDITIONAL_REVIEW_REQUIRED`, `ANALYTICAL_REVIEW_READY`, `ITEM_SELECTION_REQUIRED`, `ANALYSIS_INCOMPATIBLE`, `READY_FOR_HANDOFF`, `HANDOFF_CONFIRMED`.

`BLOCKED` and `INSUFFICIENT_EVIDENCE` never permit handoff. Conditional results use the versioned warning-disposition matrix. Unknown warnings fail closed.

## Identity

Handoff binds upload hash, schema and alias versions, event, RFQ number/item, canonical and display currency, evaluation date/source, findings, manifest and confirmation digests. Any context change invalidates handoff.

## Confirmation

High-risk header mappings are never preconfirmed. Event and RFQ item selection are explicit. The final acknowledgement confirms review of mappings, findings, evidence, currency provenance, compatibility limitations and the exact dataset identity.
