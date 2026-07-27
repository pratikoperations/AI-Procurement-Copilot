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
- Visual evidence, subject to Build Group C approval
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
- this release record.

Documentation implementation head: `9faeee7358ec2945b3aaea68064df518102e0ac3`

Quality Checks run 463, run ID `30247055209`, passed dependency installation, Python compilation, the complete regression suite and canonical Streamlit smoke with 0 failures. A final quality run on the evidence-recording head is required before owner approval.

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
- Mobile screenshots reviewed at 360, 390 and 412 px plus tablet and desktop
- Public screenshots contain no Interview Guide
- README and docs pass claim-safety review
- Final changed-file audit confirms no excluded logic files
- Owner explicitly authorizes ready-for-review and merge

## Known limitations

The system remains a portfolio demonstration. It has not been validated for production security, enterprise scale, live ERP connectivity, live organizational data or realized business outcomes.

## Relationship to v1.1

v1.2 does not amend or reclassify v1.1. The completed v1.1 release remains permanently preserved at its frozen SHA, while v1.2 adds a controlled presentation and documentation layer.