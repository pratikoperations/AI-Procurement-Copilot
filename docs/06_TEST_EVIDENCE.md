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

Approved head: `8b113a195e5a742c6bf2fe2785d79390de8ce17a`

Quality Checks run 453 passed dependency installation, compilation, the complete regression suite and canonical Streamlit smoke. No procurement-engine or ERP-foundation file was changed.

## Build Group B evidence

Approved head: `a5e4c97fb42af134bced25706b8f1dc7e12a0971`

Quality Checks run 465, run ID `30247178739`, passed dependency installation, Python compilation, the complete regression suite and canonical Streamlit smoke with 0 failures.

## Build Group C evidence

Visual implementation head: `6ee510265b0ffb124a1738a4959d92fc839ba0ac`

Quality Checks run 482, run ID `30249851991`, passed:

- dependency installation;
- Python compilation;
- complete regression suite;
- canonical Streamlit smoke.

Failures: 0. The available workflow summary does not expose the exact pytest total, so no unsupported numerical test count is recorded.

## Visual evidence boundaries

- The SVG application views use synthetic, generic content and are illustrative representations of the implemented workflow.
- They are not direct captures of the final hosted v1.2 candidate.
- Actual hosted and mobile captures remain required before release.
- Automated tests do not prove pixel-level rendering, production security, enterprise scale, live ERP integration or business adoption.

## Canonical sources

Detailed historical evidence remains in the existing QA, recovery, validation and planning records. This document is the portfolio-facing index, not a replacement for those records.
