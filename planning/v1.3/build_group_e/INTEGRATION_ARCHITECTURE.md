# Build Group E Integration Architecture

Baseline: `515c96e07da50d71b770e4b9aba47bb60c489de6`

## Routes

1. Synthetic Demo — unchanged existing route.
2. Upload RFQ CSV/Excel — unchanged legacy fuzzy-mapping and USD-normalization route.
3. Governed v1.3 Workbook Review Preview — Build C adapter, mapping review, sourcing-event and RFQ-item selection, Build D normalization, findings, evidence and provenance review.

## Review-only boundary

Governed data always returns `dataframe=None`, `analysis_handoff_allowed=False`, and terminates before validation, scoring, TCO, recommendation, allocation or negotiation. It never falls through to demo or legacy data.

`GOVERNED_RANKING_INPUTS_NOT_CANONICAL` is a compatibility-blocking finding. Adapter `original_values` and ignored columns remain provenance-only and are never promoted into analytical inputs.

## Currency

Workbook `BASE_CURRENCY` remains the Build D review comparison currency. USD, INR and other governed source currencies are preserved with source price, FX rate/date, normalized review value and row provenance. No non-USD review value is labelled USD. USD, INR and Both remain display choices; they do not enable analytical handoff.

## Session isolation

The controller hashes uploaded workbook bytes. A changed hash clears mapping confirmations, event and item selections, warning acknowledgements and any former handoff state before those values are used. Same-file reruns preserve the current review context.

## Future dependency

A separately authorized Build B/C canonical schema extension is required before frozen-engine ranking fields can support governed analytical handoff.

## Claims

The global application remains v1.2. The capability is a governed v1.3 workbook-review preview, not a production release, autonomous award process, deployment or live ERP integration.
