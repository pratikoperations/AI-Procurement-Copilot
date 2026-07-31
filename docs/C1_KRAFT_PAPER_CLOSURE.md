# Category Expansion C1 — Kraft Paper Controlled Closure Record

## Purpose

This record documents the repository, code, automated-assurance and preview-assurance closure of Category Expansion C1 — Kraft Paper. It does not authorize merge, production deployment, live paper-index integration, ERP write-back, autonomous sourcing, supplier approval, award execution, chain-of-custody certification or realized-savings claims.

## Controlled baselines

- Repository: `pratikoperations/AI-Procurement-Copilot`
- Pull request: PR #31 — `Category Expansion C1 — Kraft Paper`
- Frozen base branch: `main`
- Frozen base SHA: `ce7c6d09aaa8b022c3de35da1800b94b9dcd7670`
- Controlled feature branch: `agent/category-expansion-c1-kraft-paper`
- Documentation-authorization starting head: `626f33742480e5a6f9f5c9cd5b0f085927e0a666`
- PR status at documentation authorization: open, draft, unmerged and mergeable

The frozen main baseline and all historical S1 records remain unchanged by this closure work.

## Delivered C1 scope

C1 adds Kraft Paper as a controlled commodity under Raw Material Procurement only. It does not rewrite the existing Corrugated Board engine.

Delivered capability includes:

- fail-closed routing for unsupported raw-material commodities;
- controlled Recycled Kraft and Virgin Kraft profiles;
- governed GSM profiles: 120, 150 and 180;
- governed strength profiles: 18 BF, 22 BF and 28 BF;
- three synthetic suppliers:
  - Western Fibre Mills;
  - National Kraft Industries;
  - Circular Paperworks Ltd;
- kg as the canonical quantity and comparison basis;
- paper-specific validation, risk, scoring, allocation and scenario handling;
- controlled linkage to Corrugated Board assumption review without automatic Corrugated Board recalculation.

## Category and commodity routing

Kraft Paper is registered only under:

- Category: `Raw Material Procurement`
- Commodity: `Kraft Paper`

Kraft-specific assumptions are shown only for that route. Packaging Procurement and other raw-material commodities retain their governed category identity and behaviour.

Unsupported raw-material commodities fail closed rather than silently using a generic or unrelated cost model.

## Controlled Kraft profiles

The public demonstration uses synthetic, governed profile assumptions rather than live market specifications.

Profile controls include:

- fibre basis: Recycled Kraft or Virgin Kraft;
- GSM: 120, 150 or 180;
- strength grade: 18 BF, 22 BF or 28 BF;
- controlled profile-availability treatment;
- controlled paper-index reference;
- controlled mill/producer premium;
- freight;
- supplier margin;
- relevant paper-risk indicators.

GSM-related premium treatment represents controlled mill/profile availability. It is not represented as a physical consumption law.

## Kraft should-cost structure

The Kraft Paper should-cost model separates:

- Paper Index;
- Mill / Producer Premium;
- Freight;
- Duty / Import Cost where applicable;
- Grade / Profile Availability Premium;
- Supplier Margin.

The model retains kg as the calculation basis. Business-facing values may be displayed in USD, INR or Both according to existing currency governance.

## Validation controls

C1 validation is category- and commodity-aware and includes fail-closed treatment for material inconsistency and invalid paper inputs.

Controlled checks cover:

- Material presence and consistency;
- Kraft Paper category/commodity context;
- numeric, integral and controlled GSM values;
- controlled BF/strength grade;
- required kg Unit;
- positive and bounded moisture;
- bounded mill allocation;
- bounded fibre availability;
- bounded quality continuity;
- raw-cost input completeness, finiteness and non-negative values;
- controlled Corrugated Board linkage values.

Blocking defects stop analytical execution. Non-blocking paper risks remain visible for human procurement and technical review.

## Kraft risk controls

C1 integrates four paper-specific risk families into the decision path:

- Kraft mill allocation risk;
- Kraft moisture and yield risk;
- Kraft fibre availability risk;
- Kraft quality continuity risk.

These indicators influence risk scoring, TCO treatment, recommendation ordering, failure probability and allocation eligibility. They are decision-support controls, not laboratory, mill or certification evidence.

## Technical eligibility

Supplier-level technical eligibility is calculated and used by recommendation and allocation logic.

Business-facing outputs expose:

- `Eligible`;
- `Ineligible`;
- `Not assessed`.

Technically ineligible suppliers are excluded from governed standard and optimized allocation. Human procurement and technical approval remain mandatory.

## Allocation behaviour

C1 preserves both governed allocation paths:

- standard recommended allocation;
- optimized allocation with primary and continuity roles.

Allocation remains constraint-aware and excludes technically ineligible suppliers. The application does not execute awards, contracts, purchase orders or ERP transactions.

## Scenarios

C1 adds controlled paper-specific scenarios including:

- `Paper Price +20%`;
- `Mill / Fibre Continuity Stress`.

Scenario outputs remain analytical and provisional. They do not constitute live market forecasts or autonomous award decisions.

## Quantity-basis governance

Kilograms remain the canonical calculation unit for Kraft Paper.

The display-only tonne equivalent is governed as:

- 1,000 kg = 1 metric tonne;
- 500,000 kg = 500 metric tonnes;
- fractional tonne values use trimmed precision;
- piece and non-kg units do not receive an incorrect tonne conversion.

The final business-facing caption is:

`Canonical quantity basis: 500,000 kg (500 metric tonnes)`

The quantity-display correction did not alter annual volume, should-cost, TCO, scoring, allocation, scenario or export calculations.

## UX corrections

Final C1 UX hardening delivered:

- supplier-level `Technical Eligibility` in the Supplier RFQ Decision Snapshot;
- supplier-level `Technical Eligibility` in Supplier Intelligence comparison;
- controlled readable wrapping of the long `Raw Material Procurement` category metric;
- unambiguous metric-tonne display without unnecessary trailing zeros.

The category value itself remains unchanged. Styling is presentation-only and scoped to metric values inside Streamlit expanders.

## Automated assurance

Final governed evidence for implementation head `626f33742480e5a6f9f5c9cd5b0f085927e0a666`:

- Workflow: Quality Checks
- Run number: #648
- Run ID: `30614642110`
- Job ID: `91104910011`
- Python compilation: passed
- Regression suite: 493 passed
- Failures: 0
- Errors: 0
- Warning: one pre-existing pandas FutureWarning in adversarial-input testing
- Canonical Streamlit smoke test: passed

Focused assurance covers Kraft routing, profiles, validation, should-cost, risk, scoring, eligibility, allocation, scenarios, UX presentation and quantity-basis handling.

## Preview assurance

A separate Streamlit Community Cloud preview was deployed from:

- Branch: `agent/category-expansion-c1-kraft-paper`
- Entrypoint: `app.py`

Preview evidence confirmed:

- Raw Material Procurement → Kraft Paper routing;
- Kraft assumptions and controlled profiles;
- should-cost output;
- the three synthetic suppliers;
- lowest-price versus best-value narrative;
- category-metric readability;
- non-Kraft Corrugated Board workflow non-regression;
- application startup without visible runtime exception.

The deployment log identifies the branch but does not print the exact deployed commit SHA. Exact SHA assurance is therefore established through the unchanged PR head plus branch-deployment evidence.

Code, focused tests, full regression and Streamlit smoke conclusively verify the final quantity caption and Technical Eligibility output. A post-refresh screenshot is optional presentation evidence rather than a code-correctness requirement.

## Claim boundaries

Safe claims:

- controlled synthetic Kraft Paper demonstration;
- category-aware should-cost, TCO, risk and scenario support;
- supplier-level technical eligibility;
- eligibility-aware allocation;
- governed human decision support;
- automated regression and startup assurance.

Not claimed:

- production readiness;
- live paper index or market pricing;
- live ERP integration or write-back;
- autonomous sourcing, supplier approval or award;
- realized savings;
- chain-of-custody, mill, quality or laboratory certification;
- formal WCAG or device certification;
- enterprise-scale operational performance.

## Residual limitations

- Wide supplier tables require internal horizontal scrolling on narrow viewports.
- Long Supplier Intelligence recommendation-status text may wrap heavily on constrained screens.
- Streamlit deployment logs identify the branch but not the exact deployed SHA.
- Manual opening of every CSV, JSON and Excel download is not represented as completed certification.
- A future all-suppliers-technically-ineligible scenario should use an explicit no-eligible-winner presentation.
- Formal accessibility and browser-device certification remain outside portfolio scope.

## Governance status

- PR #31 remains draft.
- No merge, tag, release or deployment promotion is authorized by this document.
- Main remains untouched.
- The existing main Streamlit deployment remains untouched.
- The separate C1 preview remains assurance infrastructure only.
- Human procurement and technical approval remain mandatory.

## Closure status

**Category Expansion C1 — Kraft Paper is complete at the implementation, code-review, automated-assurance and controlled preview-assurance levels. Documentation closure does not authorize PR readiness, merge, tag, release or production deployment. A separate final ready-for-review audit and explicit owner authorization remain required.**
