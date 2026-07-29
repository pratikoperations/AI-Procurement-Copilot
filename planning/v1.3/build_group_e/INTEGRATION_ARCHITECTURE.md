# Build Group E Integration Architecture

Baseline: `515c96e07da50d71b770e4b9aba47bb60c489de6`

## Routes

1. Synthetic Demo — unchanged existing route.
2. Upload RFQ CSV/Excel — unchanged legacy fuzzy-mapping and USD-normalization route.
3. Governed v1.3 Workbook Review Preview — Build C adapter, human review, Build D orchestration, compatibility assessment, explicit handoff.

## Boundary

Governed data produces either no DataFrame and a governed stop state, or one exact-identity, handoff-confirmed compatibility DataFrame. It never falls through to demo or legacy data.

Governed data bypasses `normalize_rfq_dataframe` and `normalize_comparison_basis`. Existing engines remain unchanged.

## Currency

Source quotation currency, canonical engine currency and display currency are separate. Source currencies may include USD, INR and other explicitly governed currencies. Source values and FX provenance are preserved. Existing engines receive canonical USD only. Display and exports may use USD, INR or Both; Both is dual presentation of one analytical result.

## Initial scope

One workbook, one selected sourcing event, one selected RFQ item, one comparison UOM, and at least two eligible suppliers.

## Claims

The global application remains v1.2. The new capability is labelled a governed v1.3 workbook-review preview. It does not claim production deployment, autonomous award, live ERP integration or realized savings.
