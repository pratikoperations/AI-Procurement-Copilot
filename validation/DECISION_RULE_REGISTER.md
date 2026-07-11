# Decision Rule Register

| Rule | Trigger | Output | Priority | Exception handling | Human review | Failure state |
|---|---|---|---:|---|---|---|
| RFQ schema gate | Required columns missing or invalid | Stop scoring | 1 | Correct file or mapping | Mandatory | Blocked |
| Positive price gate | Quote ≤0 | Stop recommendation | 1 | Correct source value | Mandatory | Blocked |
| Positive volume gate | Annual volume ≤0 | Stop recommendation | 1 | Enter valid demand | Mandatory | Blocked |
| Currency consistency | More than one comparison currency | Stop recommendation | 1 | Convert using approved FX basis | Mandatory | Blocked |
| Unit consistency | More than one UOM | Stop recommendation | 1 | Normalize to approved UOM | Mandatory | Blocked |
| Capacity sufficiency | Total capacity < annual demand | Stop allocation | 1 | Add capacity, alternate supplier or demand plan | Mandatory | Blocked |
| Allocation total | Allocation ≠100% | Stop recommendation | 1 | Recalculate allocation | Mandatory | Blocked |
| Allocation capacity | Supplier allocated demand > capacity | Stop recommendation | 1 | Reallocate or validate capacity | Mandatory | Blocked |
| Data confidence <50 | Completeness score below 50 | No final recommendation | 2 | Close critical gaps | Mandatory | Insufficient Data |
| Data confidence 50–69 | Completeness score 50–69 | Provisional analysis | 3 | Human validation and evidence closure | Mandatory | Human Review Required |
| Data confidence 70–84 | Completeness score 70–84 | Conditional recommendation | 4 | Document conditions | Mandatory | Eligible With Conditions |
| Data confidence ≥85 | Strong completeness and no blocking issue | Eligible recommendation | 5 | Standard governance | Mandatory | Eligible |
| Minimum risk threshold | No supplier meets configured threshold | Stop award recommendation | 2 | Mitigation or documented exception | Mandatory | Blocked |
| Single supplier | Only one supplier | Single-source warning | 4 | Continuity and market test required | Mandatory | Eligible With Conditions |
| Duplicate supplier | Duplicate normalized names | Consolidation warning | 3 | Confirm separate sites/legal entities | Mandatory | Eligible With Conditions |
| Strategic classification | Strong strategic index and criticality | Strategic | 6 | Cannot override critical financial/risk status silently | Mandatory | Warning/Blocked |
| Exit candidate | Performance, risk or financial health below threshold | Exit Candidate | 5 | Transition plan and approval | Mandatory | Human Review Required |
| Best value ranking | Highest governed multi-factor result | Best Value Supplier | 7 | Eligibility gate supersedes ranking | Mandatory | Withheld when blocked |
| Executive narrative | Eligibility permits award language | Board-ready recommendation | 8 | Replace with validation-withheld notice | Mandatory | Withheld |

## Priority rule

Lower priority number means the rule is applied earlier. Safety and data-validity gates always supersede scoring, ranking, narrative and presentation rules.
