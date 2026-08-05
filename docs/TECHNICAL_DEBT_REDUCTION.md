# Technical Debt Reduction Pack

## Status

Bounded hardening programme for the interview and portfolio application.

## Frozen base

- Authoritative base SHA: `013933c116bba88c349e6df2ec444a66f71cfbf9`
- Runtime patch removal: deferred
- Feature changes: prohibited

## Current runtime dependency map

`sitecustomize.py` is an import-time presentation bootstrap. It currently coordinates:

1. global SourceMate mounting after Streamlit page configuration;
2. publication of supplier scores and assumptions into SourceMate context;
3. insertion of the decision-clarity layer before the detailed dashboard;
4. Procurement Intelligence display-currency formatting;
5. Calculation Explorer business-readable evidence formatting;
6. the established SourceMate public intent catalogue.

These dependencies are intentionally retained during this pack. Any future removal requires a separate architecture programme and route-by-route migration.

## Hardening scope

- bounded exception handling and structured diagnostic events;
- architecture dependency documentation;
- property-based tests for invariants;
- cross-surface contract tests;
- Ruff quality checks;
- targeted mypy checks;
- dependency vulnerability audit.

## Exclusions

- no runtime monkey-patching removal;
- no calculation or scoring changes;
- no qualification, recommendation or allocation changes;
- no RFQ or export changes;
- no SourceMate knowledge expansion;
- no new procurement capability;
- no production or ERP integration.

## Quality gates

The pack is complete only when:

- existing regression tests pass;
- Streamlit smoke passes;
- Ruff passes on the governed target set;
- targeted mypy checks pass;
- dependency audit has no unresolved high-severity finding, or an explicit documented exception exists;
- new property and cross-surface contract tests pass;
- hosted presentation behavior remains unchanged.
