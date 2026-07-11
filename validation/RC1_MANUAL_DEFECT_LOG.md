# Build 1.0 RC1 — Manual Defect Log

## Purpose

Record all defects, confusing outputs, unrealistic recommendations and usability issues found during RC1 manual validation.

## Severity

- Critical — unsafe or incorrect award outcome; application unusable
- Major — material decision distortion or release-blocking workflow failure
- Moderate — meaningful usability, clarity or credibility issue
- Minor — cosmetic or low-impact issue
- Enhancement — useful but not required for v1.0

## Defects

| ID | Test ID | Category | Device | Description | Severity | Expected behavior | Actual behavior | Status | Release blocker | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| RC1-DEF-001 | RC1-B12 | Packaging | Android / Chrome | Financial view previously showed 100/100 with 0% evidence | Major | Insufficient Data with capped provisional score | Fixed in Build 0.9.6.1; live screenshot shows 50/100 cap | Closed | No | Live screenshot |
| RC1-DEF-002 | RC1-B13 | Packaging | Android / Chrome | ESG evidence could overstate maturity | Major | Completeness-governed score and maturity | Fixed; live screenshot shows Limited Evidence and 70/100 cap | Closed | No | Live screenshot |
| RC1-DEF-003 | RC1-B14 | Packaging | Android / Chrome | Innovation evidence could overstate maturity | Major | Insufficient Data and Basic ceiling | Fixed; live screenshot shows 50/100 and Basic | Closed | No | Live screenshot |
| RC1-DEF-004 | RC1-B10–B15 | Packaging | Android / Chrome | Raw JSON and code-like Supplier Intelligence presentation | Moderate | Executive-readable cards, charts and matrices | Fixed in Build 0.9.6.1 and live validated | Closed | No | Live screenshots |

## Open Defects

None recorded yet in RC1 manual testing.

## Rule

Every new Critical or Major defect requires:

1. Root-cause analysis
2. Corrective commit
3. Regression test
4. Green CI
5. Live retest
6. Release-blocker decision
