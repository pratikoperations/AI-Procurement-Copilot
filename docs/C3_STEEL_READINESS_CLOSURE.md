# C3 Steel Sheets and Coils — Readiness Closure

## Status

C3.0 through C3.7 were implemented on PR #33 and merged into `main` at merge commit `d3ad5d05dd874e4916ba4f9190ce98809e0ac10e`.

The governed pre-merge base was `0b310b4e97e0c92112089929fca150d7f183ecc8`. The retained feature branch is `agent/category-expansion-c3-steel` at feature head `def95119c2145f4391b61b5d4c6acaca2179248b`.

## Final verification evidence

- Quality Checks run: 749
- Run ID: `30665231192`
- Job ID: `91270565010`
- Python compilation: passed
- Full regression: 849 passed; 0 failures; 0 errors
- Canonical Streamlit smoke test: passed
- Warning state: one pre-existing pandas FutureWarning
- Deployment status: unchanged

## Implemented scope

- three controlled Steel profiles;
- controlled synthetic supplier data;
- USD/kg normalization for USD and INR quotations;
- dedicated should-cost model;
- fail-closed technical eligibility;
- separate generic and Steel-specific risk;
- eligible-only scoring and human-governed recommendation;
- exactly seven governed scenarios;
- standard and optimized capacity-constrained allocation;
- dependent-state UX for profile, sourcing route, duty, zinc, paint, substitution and display mode;
- isolated Steel application route that stops before generic downstream outputs;
- nine-sheet governed Excel workbook;
- strict JSON under `steel_governance` with `allow_nan=False`;
- separate numeric USD and INR fields;
- explicit human-approval, no-autonomous-award, no-engineering-approval and synthetic-data boundaries.

## Historical record

The C3.0 contract and original activity-ledger statements described features as future and unauthorized at that phase. Those statements remain historical phase evidence and do not describe the merged C3.7 implementation state.

## Readiness boundaries

This showcase is decision support only. It does not provide metallurgical certification, engineering substitution approval, mill-test-certificate authentication, live commodity or FX data, ERP write-back, production allocation, autonomous award or realised-savings evidence.

## Remaining limitations

- No complete hosted browser and mobile walkthrough has been recorded after the merge.
- No full browser-driven AppTest covers every interactive Steel transition.
- Some generic calculations occur before the Steel route reaches its `st.stop()` boundary.
- Supplier, capacity, FX, duty and market assumptions remain controlled synthetic demonstration inputs.

## Branch and release governance

PR #33 is merged. Retain `agent/category-expansion-c3-steel` temporarily for rollback reference and audit comparison. Deployment, tag, release and feature-branch deletion remain separately governed actions.
