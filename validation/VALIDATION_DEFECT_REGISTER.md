# Validation Defect Register

## Severity definitions

- **Critical:** Can produce an incorrect award or unsafe decision.
- **Major:** Materially distorts cost, risk, allocation or classification.
- **Moderate:** Reduces usability or clarity without invalidating the decision.
- **Minor:** Cosmetic or low impact.

| Defect ID | Source | Module | Description | Severity | Corrective action | Status | Retest | Release blocker |
|---|---|---|---|---|---|---|---|---|
| VAL-001 | Internal validation | app.py | Final award language lacked a central eligibility gate | Critical | Added eligibility and safe narrative withholding | Closed | Passed #150–#208 | No |
| VAL-002 | Internal validation | Supplier 360 | Defaults could create false confidence | Major | Connected defaults to data confidence | Closed | Passed #150–#208 | No |
| VAL-003 | Internal validation | Allocation | Capacity not centrally verified | Critical | Added independent capacity and 100% checks | Closed | Passed #150–#208 | No |
| VAL-004 | Internal validation | Currency/UOM | Mixed comparison basis could enter analysis | Critical | Added currency/UOM blockers | Closed | Passed #150–#208 | No |
| VAL-005 | Internal validation | Percentages | Decimal versus whole-number ambiguity | Major | Added warning and tests | Closed | Passed #150–#208 | No |
| VAL-006 | Live validation | Supplier Intelligence UI | Raw structured output exposed | Moderate | Replaced with executive UI components | Closed | Passed CI/live | No |
| VAL-007 | Live validation | Financial engine | 100/100 shown with 0% evidence | Major | Added evidence caps and due diligence | Closed | Passed CI/live | No |
| VAL-008 | Live validation | ESG engine | Weak evidence could overstate maturity | Major | Added completeness caps | Closed | Passed CI/live | No |
| VAL-009 | Live validation | Innovation engine | Weak evidence could overstate maturity | Major | Added completeness caps | Closed | Passed CI/live | No |
| RC1-UX-001 | RC1 review | dashboard.py | Technical chart legends | Minor | Executive chart labels | Fixed | Pending final live review | No |
| RC1-UX-002 | RC1 review | recommendation engine | Developer-style explanation | Minor | Business rationale by role | Fixed | Pending final live review | No |
| RC1-UX-003 | RC1 review | dashboard.py | Packaging heading in Raw Material view | Minor | Category-aware heading | Fixed | Pending final live review | No |
| RC1-DEF-005 | Download review | Currency governance | INR metadata under USD-labelled value | Major | Preserve original quotation and normalize explicitly | Fixed | Pending final download retest | Yes |
| RC1-DEF-006 | Download review | Executive outputs | Raw Material email used packaging terms and units | Major | Category-aware communication | Fixed | Pending final download retest | Yes |
| RC1-DEF-007 | Download review | Recommendation engine | Rankings ignored governed evidence status | Major | Use displayed scores and evidence qualification | Fixed | Pending final download retest | Yes |
| RC1-DEF-008 | Download review | Cross-output governance | Blocked memo and email were inconsistent | Moderate | Eligibility-aware communication | Fixed | Pending final download retest | Yes |
| RC1-DEF-009 | Download review | UI/exports | Risk Score terminology was ambiguous | Moderate | Rename visible label to Risk Resilience Score | Fixed | Pending final live/download retest | No |
| RC1-DEF-010 | Download review | Recommendation engine | Development and Exit roles could coexist | Moderate | Enforce candidate precedence | Fixed | Pending final live retest | Yes |
| RC1-DEF-011 | Download review | Exports | Readable files exposed technical fields | Moderate | Add readable report builders and separate audit data | Fixed | Pending download inspection | Yes |
| RC1-DEF-012 | Manual Excel review | exports.py / supplier_comparison.py | RFQ and governed Supplier Intelligence scores used the same visible labels | Major | Differentiate RFQ scores and expose governed Supplier 360 scores | Fixed | Pending RC1.2.2 CI and corrected export review | Yes |
| RC1-DEF-013 | Manual Excel review | scenario.py / tco.py / raw_material_tco.py | Freight +50% did not change Raw Material TCO for the DDP winner | Major | Add explicit embedded-freight pass-through during freight stress | Fixed | Pending RC1.2.2 CI and scenario retest | Yes |
| RC1-DEF-014 | Manual Excel review | scenario.py | Scenario export retained Risk Score and Advanced TCO Unit USD | Minor | Use Risk Resilience Score and category-aware TCO headings | Fixed | Pending corrected Excel review | No |

## Release rule

No open Critical defect or unmitigated Major defect is permitted for Portfolio Edition v1.0 approval.

## Current status

RC1-DEF-012 through RC1-DEF-014 have corrective implementation in Build 1.0 RC1.2.2 but remain open until GitHub Actions, Streamlit smoke testing, and manual export retesting pass. Earlier RC1 defects also remain subject to final closure evidence.
