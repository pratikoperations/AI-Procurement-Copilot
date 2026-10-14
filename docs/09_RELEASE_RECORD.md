# AI Procurement Copilot — Release and Controlled-Evolution Record

## Historical v1.2 release identity

- Release: **AI Procurement Copilot v1.2 — Portfolio Presentation Release**
- Pull request: PR #14
- Release branch: `release/v1.2-portfolio-presentation`
- Frozen v1.1 baseline: `b85cd37aaae709058eb15350d680b18c03da46ba`
- Reviewed v1.2 implementation head: `6838effb6f47b327419d7801c01c6284514f0cbb`
- Final v1.2 documentation head: `e61a26eef65ffd7e6bd015ae2168e26a5c42747f`
- Final v1.2 merge commit and frozen baseline: `4803b1d72fa8a6509d9d7faf0e9decc677c447be`
- Historical release status: **completed, merged and frozen**
- Tag: **not created by deliberate release decision**
- GitHub Release: **not created by deliberate release decision**

The v1.2 release remains historically frozen. Later separately authorized repository work does not rewrite or invalidate that release record.

## v1.2 purpose and delivered scope

The v1.2 release improved recruiter comprehension, hiring-manager review, technical verification and mobile presentation without expanding procurement-engine or ERP-foundation scope.

Delivered scope included:

- executive-first public landing view;
- compact native section selector;
- seven governed sourcing sections;
- grouped business-facing and machine-readable downloads;
- recruiter and hiring-manager documentation;
- user workflow, architecture, validation, test and governance summaries;
- synthetic visual package and screen-recording assets;
- responsive hosted verification;
- claim-safety and release-governance closure.

## v1.2 quality evidence

- Quality Checks run #492, run ID `30434354425`: success;
- 226 regression tests passed with 0 failures and 0 errors;
- canonical Streamlit smoke test passed;
- final documentation-only run #493, run ID `30440102419`: success;
- PR #14 merged to `4803b1d72fa8a6509d9d7faf0e9decc677c447be`.

## Controlled evolution after the frozen v1.2 baseline

After v1.2 closure, separate owner authorizations added controlled repository capabilities and quality hardening. These additions are not retroactively classified as part of the frozen v1.2 release.

### Governed workbook and analytical-handoff foundation

The repository subsequently added:

- versioned v1.3 workbook contracts and synthetic templates;
- governed workbook adapter and provenance controls;
- orchestration, normalization and evidence aggregation;
- review-only Streamlit integration;
- canonical supplier-ranking inputs;
- a controlled analytical handoff that remains governed and default-off unless explicitly enabled.

These builds preserve human approval and do not create live ERP integration, write-back or autonomous awards.

### Build Group S1 quality hardening

| Phase | Scope | Final status |
|---|---|---|
| S1.1 | Presentation-system consistency | Complete |
| S1.2 | Business-facing validation guidance | Complete |
| S1.3 | Mobile responsiveness | Complete |
| S1.4 | Export runtime efficiency | Complete |
| S1.5 | Accessibility, final UX assurance and release reconciliation | Complete |
| S1.5.1 | Hosted responsive containment correction | Complete |

Authoritative S1.5.1 starting base:

`9fbc3bd1d278f53b195b07768a71149e56b5b355`

S1.5.1 corrective evidence:

- corrective pull request: PR #29;
- feature head: `d3056f52b0adadb9014cd6c52d6718e7bd14e4c6`;
- final merge commit and authoritative main SHA: `e7d3d337d4bfeeb0b750372b6c1cf8537959f368`;
- Quality Checks run #621, run ID `30572516967`: success;
- 447 regression tests passed with 0 failures and 0 errors;
- one existing pandas FutureWarning remained in adversarial-input testing;
- canonical Streamlit smoke test passed;
- exact corrective scope: `modules/ui_theme.py` and `tests/test_s1_5_accessibility.py`.

Code and automated verification established that:

- responsive CSS is applied through `render_sidebar()` calling `apply_ui_theme()`;
- viewport and generated Streamlit wrappers are width-bounded;
- metric labels, values and deltas are configured to wrap without ellipsis;
- tablet columns wrap and mobile columns stack;
- wide dataframes and tables retain internal horizontal scrolling;
- visible `:focus-visible` styling is present;
- reduced-motion preferences are handled;
- governed-route and analytical-handoff feature flags remain disabled by default;
- no analytical, validation, scoring, threshold, workbook-contract or governance logic changed in S1.5.1.

Automated checks and source inspection do not constitute formal browser-device certification or formal WCAG certification. Browser-computed layout, focus appearance and physical scrollbar behavior remain matters for manual visual review where required.

## Logistics & Freight controlled evolution — October 2026

A separately governed Logistics & Freight programme added Domestic Road Transportation — Full Truck Load (FTL) as a Foundation Preview.

Delivered stages:

- LOGISTICS-0 — governed lane, carrier, commercial, evidence and compatibility foundation;
- LOGISTICS-1 — deterministic INR freight normalization;
- LOGISTICS-2 — buyer-threshold carrier performance and risk evaluation without composite scoring or ranking;
- LOGISTICS-3 — human-proposed carrier allocation and demand-scenario evaluation without automatic share optimization;
- LOGISTICS-4 — explicit buyer negotiation positions, transparent commercial deltas and decision presentation without autonomous negotiation or award;
- LOGISTICS-5 — SourceMate evidence integration and interview/demo polish.

Authoritative LOGISTICS-5 closure evidence before final documentation reconciliation:

- PR #119 source head: `eb5f32dda920b9eeb01b08f930fb9f80dbec8be0`;
- PR Quality Checks run #1167: SUCCESS;
- PR Mobile Browser Acceptance run #173: SUCCESS;
- merged main SHA: `80f6330ccb1a98fe3410359761505831efef9ef8`;
- post-merge Quality Checks run #1168 / run ID `38610533168`: SUCCESS.

The Logistics programme remains portfolio/interview decision support. It does not establish production TMS capability, live carrier-market data, route optimization, autonomous carrier ranking/allocation/negotiation, carrier award authority, realized savings or TMS/ERP writeback.

## Current governance boundary

The application remains:

- read-only;
- validation-gated;
- human-controlled;
- a portfolio demonstration rather than a production deployment;
- without live SAP or Oracle connectivity;
- without ERP write-back;
- without autonomous supplier approval or award execution;
- without realized-savings claims;
- without formal WCAG certification.

## Release-history preservation rule

The frozen v1.1 and v1.2 baselines remain immutable historical reference points. Controlled later builds may update the current repository and hosted application only through explicit branch, CI, review and merge authorization. Documentation must distinguish the current repository baseline from frozen historical releases.

## Tag and GitHub Release decision

No v1.2 tag or GitHub Release was created. No later tag or GitHub Release is implied by this record. Either action requires separate owner authorization.
