# Validation Defect Register

## Severity definitions

- **Critical:** Can produce an incorrect award or unsafe decision.
- **Major:** Materially distorts cost, risk, allocation or classification.
- **Moderate:** Reduces usability or clarity without invalidating the decision.
- **Minor:** Cosmetic or low impact.
- **Enhancement:** Useful future improvement.

## Finding dispositions

Accepted, Partially Accepted, Rejected, Deferred. Rejected findings require written rationale.

| Defect ID | Source | Module | Description | Severity | Business impact | Reproduction | Expected | Actual | Root cause | Corrective action | Status | Owner | Evidence | Commit | Retest | Release blocker | Disposition |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| VAL-001 | Internal validation | app.py | Final award language could appear before a dedicated eligibility gate | Critical | Polished output may imply approval despite weak data | Load incomplete or inconsistent supplier data | Withhold final award language | Recommendation path did not have central assurance gate | Missing central eligibility control | Add data confidence, rules and narrative withholding | Closed | Project owner | Build 0.9.6 safety modules | Build 0.9.6 | Passed #150–#208 | No | Accepted |
| VAL-002 | Internal validation | Supplier 360 | Defaults could create false confidence | Major | Relationship classification may look more evidence-based than it is | Use minimal optional fields | Defaults visible and confidence reduced | Defaults not connected to award eligibility | Missing cross-engine confidence measure | Include defaults in confidence | Closed | Project owner | data_confidence.py | Build 0.9.6 | Passed #150–#208 | No | Accepted |
| VAL-003 | Internal validation | Allocation | Capacity not centrally verified against share | Critical | Infeasible award split | Demand exceeds capacity | Block recommendation | No final feasibility gate | Missing post-allocation validator | Add capacity and 100% checks | Closed | Project owner | business_rule_validator.py | Build 0.9.6 | Passed #150–#208 | No | Accepted |
| VAL-004 | Internal validation | Currency/UOM | Mixed comparison basis could enter analysis | Critical | Invalid comparison | Upload mixed currency or units | Block recommendation | Normalized basis assumed | Missing consistency gate | Add currency/UOM blockers | Closed | Project owner | validation datasets | Build 0.9.6 | Passed #150–#208 | No | Accepted |
| VAL-005 | Internal validation | Percentages | Decimal versus whole-number ambiguity | Major | Distorted scores | Use 0.95 and 95 | Flag convention | Both numerically valid | Format ambiguity | Add warning and tests | Closed | Project owner | percentage_formats.csv | Build 0.9.6 | Passed #150–#208 | No | Accepted |
| VAL-006 | Live validation | Supplier Intelligence UI | Raw structured output exposed in executive interface | Moderate | App looked developer-oriented and difficult to read | Open Financial, ESG, Innovation or SRM tab | Cards, matrices, charts and readable actions | Nested payload displayed directly | Debug-style renderer remained in production UI | Replace with reusable executive UI components and readable reports | Fixed, retest pending | Project owner | supplier_intelligence_ui.py and UI tests | Build 0.9.6.1 | Pending CI/live | Yes until retest | Accepted |
| VAL-007 | Live validation | Financial engine | 100/100 and Low Risk shown with 0% financial completeness | Major | Could mislead decision-makers about supplier strength | Open supplier with defaulted financial fields | Insufficient Data, capped provisional score and due diligence | Strong score shown despite no evidence | Raw indicator not governed by evidence completeness | Add assessment status, evidence caps, displayed score and mandatory due diligence | Fixed, retest pending | Project owner | supplier_financial_engine.py and governance tests | Build 0.9.6.1 | Pending CI/live | Yes until retest | Accepted |
| VAL-008 | Build 0.9.6.1 review | ESG engine | Missing ESG evidence could support overly strong maturity | Major | Sustainability maturity could be overstated | Evaluate sparse ESG row | Score and maturity capped by completeness | Defaults influenced maturity without evidence gate | Missing evidence governance | Add completeness, capped displayed score and verification requirement | Fixed, retest pending | Project owner | supplier_esg_intelligence.py | Build 0.9.6.1 | Pending CI/live | Yes until retest | Accepted |
| VAL-009 | Build 0.9.6.1 review | Innovation engine | Missing innovation evidence could support overly strong maturity | Major | Collaboration readiness could be overstated | Evaluate sparse innovation row | Score and maturity capped by completeness | Defaults influenced maturity without evidence gate | Missing evidence governance | Add completeness, capped displayed score and verification requirement | Fixed, retest pending | Project owner | supplier_innovation_engine.py | Build 0.9.6.1 | Pending CI/live | Yes until retest | Accepted |

## Release rule

No open Critical defects and no unmitigated Major defects are permitted for Portfolio Edition v1.0 release approval.

## Current internal defect status

VAL-006 to VAL-009 are implemented but remain release blockers until Build 0.9.6.1 CI and live Streamlit validation pass.
