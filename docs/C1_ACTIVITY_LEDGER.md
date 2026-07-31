# Category Expansion C1 — Kraft Paper Activity Ledger

## Ledger purpose

This ledger records the controlled lifecycle of Category Expansion C1 — Kraft Paper. It is an additive record for PR #31 and does not amend, overwrite or reinterpret historical S1 records or frozen release baselines.

## Repository controls

- Repository: `pratikoperations/AI-Procurement-Copilot`
- Pull request: PR #31
- Base branch: `main`
- Required base SHA: `ce7c6d09aaa8b022c3de35da1800b94b9dcd7670`
- Feature branch: `agent/category-expansion-c1-kraft-paper`
- Documentation-authorization starting head: `626f33742480e5a6f9f5c9cd5b0f085927e0a666`
- Governance: draft PR; no direct main changes; no merge, tag, release or deployment promotion without separate authorization

## Controlled activity sequence

| Sequence | Activity | Evidence / outcome | Status |
|---:|---|---|---|
| 1 | Base verification | Main verified against required base SHA before controlled branch work | Complete |
| 2 | Branch control | Work performed on `agent/category-expansion-c1-kraft-paper` only | Complete |
| 3 | Initial C1 implementation | Kraft routing, profiles, should-cost, suppliers, validation, risks, scenarios and Corrugated linkage added | Complete |
| 4 | Independent code review | Material issues identified in validation, risk integration, eligibility, allocation and presentation | Complete |
| 5 | Controlled correction build | Category-aware validation, bounded paper controls, risk integration and eligibility-aware allocation implemented | Complete |
| 6 | Focused and full regression | C1 tests and full governed suite executed | Complete |
| 7 | Separate branch preview | Streamlit Community Cloud preview deployed from the C1 branch using `app.py` | Complete |
| 8 | Core preview assurance | Kraft controls, should-cost and supplier workflow observed | Complete |
| 9 | Final UX correction | Technical Eligibility exposed; long category metric wrapping controlled | Complete |
| 10 | Quantity-display review | Ambiguous `500.000 metric tonnes` presentation identified | Complete |
| 11 | Quantity-display correction | Whole tonnes rendered without unnecessary decimals; kg remains canonical | Complete |
| 12 | Final governed CI | Quality Checks #648: 493 passed; one existing warning; smoke passed | Complete |
| 13 | Documentation and ledger closure | C1 closure record and activity ledger added under controlled authorization | Complete |
| 14 | Final ready-for-review audit | Separate authorization required | Pending |
| 15 | PR readiness / merge | Separate explicit authorization required | Not authorized |
| 16 | Tag / release / deployment promotion | Separate explicit authorization required | Not authorized |

## Scope delivered

- Kraft Paper under Raw Material Procurement only
- unsupported raw-material commodities fail closed
- Recycled Kraft and Virgin Kraft profiles
- 120/150/180 GSM controls
- 18/22/28 BF controls
- paper index, mill premium, freight, grade/profile availability premium and supplier margin
- three synthetic Kraft suppliers
- paper-specific validation and risks
- supplier technical eligibility
- eligibility-aware standard and optimized allocation
- Paper Price +20% scenario
- Mill / Fibre Continuity Stress scenario
- controlled Corrugated Board assumption linkage
- kg quantity basis with clear metric-tonne equivalent
- business-facing Technical Eligibility output
- scoped category-metric readability correction

## Assurance evidence

### Final implementation head before documentation

`626f33742480e5a6f9f5c9cd5b0f085927e0a666`

### Final implementation workflow

- Workflow: Quality Checks
- Run number: #648
- Run ID: `30614642110`
- Job ID: `91104910011`
- Python compilation: passed
- Regression suite: 493 passed
- Failures: 0
- Errors: 0
- Warning: one pre-existing pandas FutureWarning in adversarial-input testing
- Streamlit smoke: passed

### Preview evidence

- Separate preview branch: `agent/category-expansion-c1-kraft-paper`
- Entrypoint: `app.py`
- Kraft category path observed
- controlled assumptions observed
- should-cost output observed
- three Kraft suppliers observed
- lowest-price versus best-value narrative observed
- category-card UX correction visually observed
- non-Kraft Corrugated Board path observed after C1 changes

## Defect and correction record

| Finding | Disposition |
|---|---|
| Unsupported raw-material routing could fall through | Corrected to fail closed |
| Kraft validation could be bypassed by inconsistent context | Corrected with category/commodity-driven validation |
| GSM and other paper controls needed stronger governance | Corrected with numeric, integral and controlled-value checks |
| Paper risks did not sufficiently influence decision outputs | Corrected across scoring, TCO, failure probability, ordering and allocation |
| Supplier technical eligibility was not visible | Corrected in supplier snapshot and Supplier Intelligence comparison |
| Long category metric wrapped excessively | Corrected with scoped presentation CSS |
| Tonne equivalent displayed as `500.000`, visually ambiguous on mobile | Corrected to `500 metric tonnes` while retaining kg calculations |

## Claim-control record

The following boundaries remain active:

- portfolio-grade synthetic demonstration only;
- no live paper price or paper index;
- no production deployment;
- no live ERP integration or write-back;
- no autonomous supplier approval or award;
- no realized-savings claim;
- no formal chain-of-custody, mill, quality or laboratory certification;
- no formal WCAG or device certification;
- human procurement and technical review mandatory.

## Historical preservation

- Historical S1 documents are not modified by this ledger.
- Frozen v1.1 and v1.2 release identities remain unchanged.
- The frozen C1 base SHA remains the historical starting point for PR #31.
- Documentation closure is additive and does not imply release status.

## Residual limitations

- Narrow screens require internal horizontal scrolling for wide tables.
- Long recommendation-status text can wrap heavily.
- Streamlit logs show branch and entrypoint but not exact deployed SHA.
- Manual opening of every export format is not represented as formal certification.
- An all-suppliers-technically-ineligible scenario should receive explicit future hardening.
- Production security, identity, access, privacy, logging and operational controls remain outside scope.

## Current gate

**C1 documentation and activity-ledger closure is complete on the controlled feature branch. PR #31 must remain draft until a separate final ready-for-review audit and explicit owner authorization are completed.**
