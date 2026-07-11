# Build 1.0 RC1 — Manual Validation Checklist

## Test Environment

- Live application: `ai-procurement-copilot.streamlit.app`
- Primary device: Android / Chrome
- Repository branch: `main`
- Expected build label: `Build 1.0 RC1.2 - Export Integrity and Category-Aware Communication Hotfix`
- Feature development: Frozen

## Phase A — Startup and Navigation

| ID | Test | Expected result | Status |
|---|---|---|---|
| RC1-A01 | Open live application | App loads without traceback | Pending RC1.2 retest |
| RC1-A02 | Confirm build label | Build 1.0 RC1.2 visible | Pending |
| RC1-A03 | Open all eight tabs | Every tab renders | Pending |
| RC1-A04 | Mobile navigation | No unusable overflow | Pending |

## Phase B — Packaging Procurement

| ID | Test | Expected result | Status |
|---|---|---|---|
| RC1-B01 | Packaging demo | USD and piece basis; no false currency block | Pending RC1.2 retest |
| RC1-B02 | Validation Assurance | Eligibility and confidence visible | Previously passed; retest pending |
| RC1-B03 | Decision Summary | Best-value logic readable | Previously passed; retest pending |
| RC1-B04 | Cost & Risk | Packaging should-cost and TCO render | Previously passed; retest pending |
| RC1-B05 | Procurement Intelligence | Strategy, allocation, risk and explainability render | Previously passed; retest pending |
| RC1-B06 | Supplier Intelligence | Readable overview and five sub-tabs | Passed before RC1.2 |
| RC1-B07 | Performance | Cards, chart, strengths, gaps and actions | Passed |
| RC1-B08 | Financial | 0% evidence does not show verified strength | Passed |
| RC1-B09 | ESG | Completeness governs score and maturity | Passed |
| RC1-B10 | Innovation | Insufficient evidence caps maturity | Passed |
| RC1-B11 | SRM | Classification and governance readable | Passed |
| RC1-B12 | Packaging email | May use printing/tooling terms and piece unit | Pending RC1.2 retest |
| RC1-B13 | Packaging downloads | Readable reports open and match screen | Pending |

## Phase C — Raw Material Procurement / PET Resin

| ID | Test | Expected result | Status |
|---|---|---|---|
| RC1-C01 | Category switch | Raw Material route loads | Pending RC1.2 retest |
| RC1-C02 | Currency and unit | USD comparison basis and kg UOM | Pending |
| RC1-C03 | Standard demo | No false mixed-currency block | Pending |
| RC1-C04 | Cost & Risk | Raw Material should-cost and TCO render | Pending |
| RC1-C05 | Supplier email | kg, IV, index, premium, COA; no printing/tooling | Pending |
| RC1-C06 | Recommendation rankings | Governed roles; no unsupported awards | Pending |
| RC1-C07 | Classification precedence | Exit and Development suppliers differ | Pending |
| RC1-C08 | Executive outputs | Eligibility status consistent | Pending |
| RC1-C09 | Downloads | Currency, unit and status match screen | Pending |

## Phase D — Currency, Safety and Stress

| ID | Test | Expected result | Status |
|---|---|---|---|
| RC1-D01 | INR quotation with valid FX | Converts to USD and preserves original values | Pending |
| RC1-D02 | Unsupported currency | Blocks before comparison | Pending |
| RC1-D03 | Mixed currency with valid FX | Normalizes to one comparison basis | Pending |
| RC1-D04 | Negative price | Blocked | Previously automated; live optional |
| RC1-D05 | Capacity shortfall | Blocked or human review required | Pending |
| RC1-D06 | Low evidence | Unsupported ESG/Innovation/Long-Term roles withheld | Pending RC1.2 retest |
| RC1-D07 | Blocked status | Screen, memo, email and narrative all withhold award | Pending |

## Phase E — Export Content Quality

| ID | File | Expected result | Status |
|---|---|---|---|
| RC1-E01 | Excel Analysis | Readable sheets plus clearly labelled audit sheet | Pending |
| RC1-E02 | Supplier Scores Report CSV | Human-readable headings; original/normalized fields | Pending |
| RC1-E03 | Supplier Comparison Report CSV | Governed scores, status and Risk Resilience Score | Pending |
| RC1-E04 | Executive Memo TXT | Eligibility-aware and category-consistent | Pending |
| RC1-E05 | Supplier Email TXT | Category and validation aware | Pending |
| RC1-E06 | Executive Narrative TXT | No final award when blocked | Pending |
| RC1-E07 | Supplier 360 Readable Report | Readable business text | Pending |
| RC1-E08 | Decision Audit Data | Machine-readable and download-only | Pending |
| RC1-E09 | Supplier 360 Audit Data | Machine-readable and download-only | Pending |

## Release Decision

RC1 may be approved only when:

- GitHub Actions are green.
- Packaging and PET Resin demos pass end to end.
- All downloadable files are opened and reviewed.
- RC1-DEF-005 through RC1-DEF-011 are closed.
- No open Critical or Major defect remains.
- Independent reviews are completed or formally waived.
- Final release-readiness score is at least 9.0/10.

## Current Position

RC1.2 implementation is complete. CI, Streamlit smoke testing, and manual download inspection are pending. Portfolio Edition v1.0 is not approved or tagged.
