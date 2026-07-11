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
| VAL-001 | Internal validation | app.py | Final award language could appear before a dedicated eligibility gate | Critical | Polished output may imply approval despite weak data | Load incomplete or inconsistent supplier data | Withhold final award language | Recommendation path did not have central assurance gate | Safety controls added after scoring but before display | Add data confidence, business rules and eligibility gate; replace narrative when blocked | Closed | Project owner | Build 0.9.6 safety modules | Build 0.9.6 commits | Passed in Quality Checks #150–#208 | No | Accepted |
| VAL-002 | Internal validation | Supplier 360 | Transparent defaults can create false confidence if not penalized | Major | Relationship classification may look more evidence-based than it is | Use RFQ with minimal optional fields | Defaults visible and confidence reduced | Defaults listed but not connected to award eligibility | Missing cross-engine confidence measure | Include defaulted fields in data-confidence score and warning | Closed | Project owner | data_confidence.py | Build 0.9.6 commits | Passed in Quality Checks #150–#208 | No | Accepted |
| VAL-003 | Internal validation | Allocation | Capacity was not centrally verified against recommended share | Critical | Infeasible award split | Demand exceeds allocated supplier capacity | Block recommendation | Optimizer and presentation did not provide final independent feasibility gate | Missing post-allocation rule validator | Add capacity and 100% allocation checks | Closed | Project owner | business_rule_validator.py | Build 0.9.6 commits | Passed in Quality Checks #150–#208 | No | Accepted |
| VAL-004 | Internal validation | Currency/UOM | Mixed currency or unit files could enter analysis without a central final gate | Critical | Invalid comparisons | Upload mixed USD/INR or kg/piece | Block recommendation | Mapping and scoring assumed normalized comparison basis | Missing cross-row consistency gate | Add mixed currency and UOM blockers | Closed | Project owner | mixed-currency dataset and tests | Build 0.9.6 commits | Passed in Quality Checks #150–#208 | No | Accepted |
| VAL-005 | Internal validation | Percentages | Decimal versus whole-number percentages can be misinterpreted | Major | Distorted risk and performance scores | Use 0.95 and 95 in same field | Flag convention for review | Both values are numerically valid in a generic 0–100 check | Source-format ambiguity | Add decimal-percentage warning and validation case | Closed | Project owner | percentage_formats.csv | Build 0.9.6 commits | Passed in Quality Checks #150–#208 | No | Accepted |

## Release rule

No open Critical defects and no unmitigated Major defects are permitted for Portfolio Edition v1.0 release approval.

## Current internal defect status

All internally identified Critical and Major Build 0.9.6 defects are closed and CI retested. External-review findings may create new defects and must be added to this register before release approval.
