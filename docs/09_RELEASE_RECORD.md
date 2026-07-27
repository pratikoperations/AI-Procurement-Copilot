# AI Procurement Copilot v1.2 — Release Record

## Release identity

- Proposed release: **AI Procurement Copilot v1.2 — Portfolio Presentation Release**
- Pull request: PR #14
- Branch: `release/v1.2-portfolio-presentation`
- State: draft, open and unmerged
- Frozen baseline: v1.1 at `b85cd37aaae709058eb15350d680b18c03da46ba`

## Release purpose

Improve recruiter comprehension, hiring-manager review, technical verification and mobile presentation without expanding procurement-engine or ERP-foundation scope.

## Approved change classes

- Presentation
- Responsive navigation
- Documentation
- Test maintenance
- Visual evidence
- Release governance

## Build Group A

Delivered:

- executive-first public landing view;
- public Interview Guide removal;
- compact native section selector;
- seven public sourcing sections;
- grouped download presentation;
- v1.2 display metadata;
- focused tests and full regression closure.

Approved head: `8b113a195e5a742c6bf2fe2785d79390de8ce17a`

## Build Group B

Delivered:

- executive-first README;
- recruiter overview;
- hiring-manager case study;
- user workflow;
- architecture summary;
- data and validation summary;
- test evidence;
- governance and limitations;
- private demo guide;
- release record.

Approved head: `a5e4c97fb42af134bced25706b8f1dc7e12a0971`

Quality Checks run 465, run ID `30247178739`, passed dependency installation, Python compilation, the complete regression suite and canonical Streamlit smoke with 0 failures.

## Build Group C

Delivered:

- hero visual;
- four-screen illustrative application-view set;
- restrained numbered annotations;
- five-stage architecture visual;
- proves / does-not-prove visual;
- visual design system;
- LinkedIn cover;
- six-slide LinkedIn carousel;
- 30–40 second screen-recording storyboard;
- LinkedIn Projects description;
- recruiter short description;
- GitHub Featured wording.

Approved head: `8387f06d376e0cb1b9ba145860ab889f3edfd36a`

Quality Checks run 488, run ID `30255807628`, passed dependency installation, Python compilation, the complete regression suite and canonical Streamlit smoke with 0 failures.

The four application-view assets are synthetic illustrative representations based on the implemented interface. They are not presented as direct hosted screenshots.

## Build Group D verification status

Completed:

- final claim-safety audit;
- README and documentation path review;
- final changed-file boundary review;
- confirmation that no procurement-engine or ERP-foundation implementation file was added by Build Groups C or D;
- confirmation of green automated quality evidence at the approved Build Group C head;
- proposed v1.2 freeze statement.

Blocked:

- authoritative hosted v1.2 preview verification;
- direct browser screenshot review;
- mobile validation at approximately 360 px, 390 px and 412 px;
- tablet and desktop validation;
- confirmation that hosted views contain no Interview Guide;
- pixel-level comparison between hosted output and illustrative assets.

No authoritative v1.2 deployment URL was found in the README, PR #14 metadata or discussion, repository search or public search during the audit. The final verification report is recorded in `docs/10_FINAL_VERIFICATION_REPORT.md`.

**Merge-readiness status: NOT READY.** PR #14 must remain draft and unmerged until the authoritative v1.2 hosted URL is supplied and all outstanding hosted and viewport checks pass.

## Explicit exclusions

- procurement-engine redesign;
- normalization redesign;
- supplier or item matching;
- new procurement-engine integration;
- time-aware analytics;
- live ERP integration;
- ERP write-back;
- autonomous sourcing or awards;
- new AI-agent functionality;
- production-readiness claims;
- realized-savings claims.

## Required pre-merge gates

- Full automated test suite green
- Canonical Streamlit smoke green
- Hosted v1.2 preview verified
- Actual mobile screenshots reviewed at 360, 390 and 412 px plus tablet and desktop
- Public hosted screenshots contain no Interview Guide
- README and docs pass claim-safety review
- Final changed-file audit confirms no excluded logic files
- Owner explicitly authorizes ready-for-review and merge

## Proposed freeze statement

> AI Procurement Copilot v1.2 is a portfolio presentation release built on the frozen v1.1 baseline. It improves executive communication, responsive navigation, documentation and public visual evidence without changing procurement-engine or ERP-foundation logic. The application remains read-only, validation-gated and human-controlled, with no claim of live ERP integration, write-back, autonomous awards, production readiness or realized savings.

## Known limitations

The system remains a portfolio demonstration. It has not been validated for production security, enterprise scale, live ERP connectivity, live organizational data or realized business outcomes. Final hosted and pixel-level mobile verification remain pending.

## Relationship to v1.1

v1.2 does not amend or reclassify v1.1. The completed v1.1 release remains permanently preserved at its frozen SHA, while v1.2 adds a controlled presentation, documentation and visual layer.
