# Build 1.0 RC1 — Manual Defect Log

## Purpose

Record all defects, confusing outputs, unrealistic recommendations, and usability issues found during RC1 manual validation.

## Defects

| ID | Area | Description | Severity | Corrective build | Status | Release blocker | Retest evidence |
|---|---|---|---|---|---|---|---|
| RC1-DEF-001 | Financial | 100/100 shown with 0% financial evidence | Major | 0.9.6.1 | Closed | No | Live screenshot |
| RC1-DEF-002 | ESG | Maturity could overstate weak evidence | Major | 0.9.6.1 | Closed | No | Live screenshot |
| RC1-DEF-003 | Innovation | Maturity could overstate weak evidence | Major | 0.9.6.1 | Closed | No | Live screenshot |
| RC1-DEF-004 | Supplier Intelligence UI | Raw JSON and code-like output | Moderate | 0.9.6.1 | Closed | No | Live screenshots |
| RC1-DEF-005 | Currency | INR metadata stored under USD-labelled comparison value | Major | 1.0 RC1.2 | Fixed; retest pending | Yes | Pending live/download retest |
| RC1-DEF-006 | Communication | Raw Material supplier email used packaging terminology and units | Major | 1.0 RC1.2 | Fixed; retest pending | Yes | Pending live/download retest |
| RC1-DEF-007 | Recommendations | Ranking roles ignored governed evidence status | Major | 1.0 RC1.2 | Fixed; retest pending | Yes | Pending live/download retest |
| RC1-DEF-008 | Cross-output consistency | Blocked memo and supplier email told different stories | Moderate | 1.0 RC1.2 | Fixed; retest pending | Yes | Pending live/download retest |
| RC1-DEF-009 | Terminology | Risk Score label was ambiguous because higher is better | Moderate | 1.0 RC1.2 | Fixed; retest pending | No | Pending live retest |
| RC1-DEF-010 | Classification | Development Candidate and Exit Candidate could coexist | Moderate | 1.0 RC1.2 | Fixed; retest pending | Yes | Pending live retest |
| RC1-DEF-011 | Exports | Readable reports exposed technical fields | Moderate | 1.0 RC1.2 | Fixed; retest pending | Yes | Pending download inspection |
| RC1-DEF-012 | Exports | RFQ and governed Supplier Intelligence scores used the same readable labels | Major | 1.0 RC1.2.2 | Fixed; retest pending | Yes | Pending corrected CSV/Excel review |
| RC1-DEF-013 | Scenarios | Freight +50% did not change Raw Material TCO for DDP winner | Major | 1.0 RC1.2.2 | Fixed; retest pending | Yes | Pending CI and scenario export review |
| RC1-DEF-014 | Terminology | Scenarios worksheet retained Risk Score and Advanced TCO Unit USD | Minor | 1.0 RC1.2.2 | Fixed; retest pending | No | Pending corrected Excel review |

## Open release blockers

RC1-DEF-005 through RC1-DEF-014 remain open until their required live and download retests are complete.

Required evidence:

1. GitHub Actions are green.
2. Streamlit smoke testing passes.
3. Standard PET Resin demo loads without false currency blocking.
4. Freight +50% increases unit and annual TCO for Packaging and Raw Material demos.
5. Readable reports clearly distinguish RFQ and governed Supplier Intelligence scores.
6. Scenario export uses Risk Resilience Score and category-aware TCO headings.
7. Downloaded files are opened and manually reviewed.
8. Screen, memo, email, narrative, CSV, Excel, and audit data remain consistent.
