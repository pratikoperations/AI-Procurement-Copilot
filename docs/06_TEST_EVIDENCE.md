# AI Procurement Copilot v1.2 — Test Evidence

## Quality approach

The repository uses automated checks to protect procurement calculations, validation controls, export integrity, UI contracts, ERP Preview boundaries and application startup.

## Covered areas

- Python compilation
- Procurement-engine regression tests
- Currency and unit integrity
- Category-specific logic
- Business-rule and recommendation eligibility
- Adversarial and external-file validation
- Supplier Intelligence and UI contracts
- Business-readable and machine-readable exports
- ERP schema, mapping, loader and structural validation
- ERP Upload Preview presenter and page smoke
- Public presentation and release-version assertions
- Canonical Streamlit startup smoke

## Build Group A evidence

Approved Build Group A head:

`8b113a195e5a742c6bf2fe2785d79390de8ce17a`

Quality Checks run 453 passed dependency installation, compilation, the complete regression suite and canonical Streamlit smoke. No procurement-engine or ERP-foundation file was changed.

## Build Group B evidence

Documentation implementation head:

`9faeee7358ec2945b3aaea68064df518102e0ac3`

Quality Checks run 463, run ID `30247055209`, passed:

- dependency installation;
- Python compilation;
- complete regression suite;
- canonical Streamlit smoke.

Failures: 0. The GitHub connector did not expose the exact pytest total in the available run summary, so no unsupported test count is recorded.

A final rerun on the evidence-recording head is required before Build Group B owner review.

## Evidence boundaries

- Automated tests prove the implemented code contracts and startup behaviour.
- They do not prove production security, enterprise scale, live ERP integration or business adoption.
- Pixel-level mobile validation requires rendered screenshots and remains a pre-merge release gate.
- Hosted deployment health must be verified against the final v1.2 candidate and cannot be inferred from historical URLs.

## Canonical sources

Detailed historical evidence remains in the existing QA, recovery, validation and planning records. This document is the portfolio-facing index, not a replacement for those records.