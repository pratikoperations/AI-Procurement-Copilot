# Build 1.0 RC1 — Manual Validation Checklist

## Purpose

Validate the live Streamlit application end to end before Portfolio Edition v1.0 release. This checklist is for release assurance only. No new business features are permitted during RC1 unless required to fix a release-blocking defect.

## Evidence Standard

For every test record:

- Pass / Fail / Not Applicable
- Device and browser
- Category and commodity
- Data source
- Screenshot or short evidence note
- Defect ID when failed

## Test Environment

- Live application: `ai-procurement-copilot.streamlit.app`
- Primary mobile device: Android / Chrome
- Secondary environment: Desktop browser when available
- Repository branch: `main`
- Expected build label: `Build 0.9.6.1 - Executive-Readable Supplier Intelligence UX Hotfix`

---

# Phase A — Startup and Navigation

| ID | Test | Expected result | Status | Evidence / defect |
|---|---|---|---|---|
| RC1-A01 | Open live application | App loads without traceback | Pending | |
| RC1-A02 | Confirm build label | Build 0.9.6.1 visible | Pending | |
| RC1-A03 | Open and close sidebar | Sidebar works without layout break | Pending | |
| RC1-A04 | Open all eight top-level tabs | Every tab renders without error | Pending | |
| RC1-A05 | Refresh application | State reloads without crash | Pending | |
| RC1-A06 | Mobile scrolling and tab navigation | No unusable overflow or blocked controls | Pending | |

---

# Phase B — Packaging Procurement Demo

Use:

- Category: Packaging Procurement
- Commodity: Corrugated Board
- Data source: Synthetic Demo
- Annual volume: 500,000
- Default scenario assumptions

| ID | Test | Expected result | Status | Evidence / defect |
|---|---|---|---|---|
| RC1-B01 | Category intelligence | Packaging engine active and correct cost/risk model shown | Pending | |
| RC1-B02 | Validation Assurance Gate | Eligibility, confidence and business-rule status visible | Pending | |
| RC1-B03 | Decision Summary | Lowest price versus best value logic readable | Pending | |
| RC1-B04 | Supplier snapshot | All suppliers and key scores visible | Pending | |
| RC1-B05 | Cost & Risk | Packaging-specific should-cost and TCO render | Pending | |
| RC1-B06 | Allocation | Allocation totals 100% | Pending | |
| RC1-B07 | Scenario table | Scenario values recompute without error | Pending | |
| RC1-B08 | Negotiation | Target, walk-away and savings outputs render | Pending | |
| RC1-B09 | Procurement Intelligence | Recommendation, strategy, allocation, risk and explainability render | Pending | |
| RC1-B10 | Supplier Intelligence overview | Executive-readable overview and chart render | Pending | |
| RC1-B11 | Performance tab | Cards, chart, strengths, gaps and actions render | Pending | |
| RC1-B12 | Financial tab | Evidence status, completeness, capped score and disclaimer render | Passed | Live screenshot confirms 0% completeness, Insufficient Data, Low evidence, 50/100 cap |
| RC1-B13 | ESG tab | Evidence status, completeness, capped score and actions render | Passed | Live screenshot confirms 50% completeness, Limited Evidence, 70/100 cap |
| RC1-B14 | Innovation tab | Evidence status, completeness, capped score and opportunities render | Passed | Live screenshot confirms 0% completeness, Insufficient Data, Basic, 50/100 cap |
| RC1-B15 | SRM tab | Classification, strategic index and governance fields render | Passed | Live screenshot confirms Preferred and 71.1/100 strategic index |
| RC1-B16 | Executive Outputs | Memo, email and explainability render without raw payloads | Pending | |
| RC1-B17 | Downloads | Excel, readable report and CSV downloads work | Pending | |
| RC1-B18 | Interview Guide | Talking points render clearly | Pending | |

---

# Phase C — Raw Material Procurement Demo

Use:

- Category: Raw Material Procurement
- Commodity: PET Resin
- Data source: Synthetic Demo
- Annual volume: 500,000
- Default scenario assumptions

| ID | Test | Expected result | Status | Evidence / defect |
|---|---|---|---|---|
| RC1-C01 | Category switch | Category changes without crash | Pending | |
| RC1-C02 | Commodity and UOM | PET Resin and kg basis displayed | Pending | |
| RC1-C03 | Category intelligence | Commodity-index, freight, duty, FX and volatility logic visible | Pending | |
| RC1-C04 | Validation Assurance Gate | No false mixed-currency or mixed-unit block | Pending | |
| RC1-C05 | Decision Summary | Raw-material suppliers rank and render | Pending | |
| RC1-C06 | Cost & Risk | Raw-material should-cost and TCO render | Pending | |
| RC1-C07 | Procurement Intelligence | Recommendation, strategy, allocation and risks render | Pending | |
| RC1-C08 | Supplier Intelligence | Overview and five sub-tabs render without raw payloads | Pending | |
| RC1-C09 | Executive Outputs | Category-appropriate narratives render | Pending | |
| RC1-C10 | Downloads | Raw-material files download successfully | Pending | |

---

# Phase D — Stress and Safety Tests

| ID | Test | Expected result | Status | Evidence / defect |
|---|---|---|---|---|
| RC1-D01 | Raw-material shock +20% | Cost and TCO change; app remains stable | Pending | |
| RC1-D02 | Freight shock +20% | TCO changes; narrative updates | Pending | |
| RC1-D03 | Combined shocks | Ranking or trade-off recomputes without error | Pending | |
| RC1-D04 | Mixed-currency validation file | Recommendation blocked | Pending | |
| RC1-D05 | Negative-value validation file | Calculation blocked with readable errors | Pending | |
| RC1-D06 | Capacity-shortfall file | Allocation blocked or human review required | Pending | |
| RC1-D07 | Single-supplier file | Single-source warning shown | Pending | |
| RC1-D08 | 50-supplier file | File loads and remains usable | Pending | |
| RC1-D09 | Missing critical fields | Final award language withheld | Pending | |
| RC1-D10 | Low evidence Supplier 360 | Strong financial, ESG or innovation claims remain capped | Passed | Packaging live screenshots confirm safeguards |

---

# Phase E — Exports and Content Quality

| ID | Test | Expected result | Status | Evidence / defect |
|---|---|---|---|---|
| RC1-E01 | Excel analysis | Downloads and opens with populated sheets | Pending | |
| RC1-E02 | Supplier comparison CSV | Downloads and contains supplier rows | Pending | |
| RC1-E03 | Supplier 360 readable report | Downloads and contains readable text | Pending | |
| RC1-E04 | Supplier 360 audit data | Download-only; not displayed in UI | Pending | |
| RC1-E05 | Executive memo | No raw field names or payload syntax | Pending | |
| RC1-E06 | Supplier email | Professional and category appropriate | Pending | |
| RC1-E07 | Executive narrative | Clear situation, analysis, recommendation, risk and next steps | Pending | |
| RC1-E08 | No raw output audit | No JSON, dictionary, raw list or snake-case label visible | Partially Passed | Supplier Intelligence screenshots passed; full app review pending |

---

# Phase F — Release Decision

RC1 may be approved only when:

- All Critical and Major defects are closed or formally mitigated.
- All mandatory tests pass.
- Packaging and Raw Material workflows pass end to end.
- Download tests pass.
- Mobile validation passes.
- Latest GitHub Actions are green.
- Independent reviews are completed or formally waived.
- Final release-readiness score is at least 9.0/10.

## Current RC1 Position

- Feature development: Frozen
- Automated CI: Green through Build 0.9.6.1 latest runs
- Packaging Supplier Intelligence governance: Partially live validated
- Full Packaging workflow: In progress
- Raw Material workflow: Pending
- Release approval: Not granted
