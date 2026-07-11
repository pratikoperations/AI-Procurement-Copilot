# Expected Result Matrix

| ID | Input condition | Category | Validation | Eligibility | Confidence | Recommendation behavior | Warning | Release blocker |
|---:|---|---|---|---|---|---|---|---|
| 01 | One supplier only | Both | Warning | Eligible With Conditions | Acceptable | Single-source only | Continuity mitigation | No |
| 02 | Identical scores | Both | Warning | Human Review Required | Acceptable | Do not imply decisive winner | Tie / sensitivity | No |
| 03 | No supplier meets risk threshold | Both | Fail | Blocked | Any | Withhold award | Risk exception required | Yes |
| 04 | No supplier meets ESG threshold | Both | Warning/Fail by policy | Human Review Required | Any | Provisional only | ESG exception | Conditional |
| 05 | Missing optional data | Both | Warning | Eligible With Conditions | Limited/Acceptable | Provisional | Defaults visible | No |
| 06 | Missing critical data | Both | Fail | Blocked | Insufficient | No recommendation | Missing fields | Yes |
| 07 | Duplicate names | Both | Warning | Eligible With Conditions | Acceptable | Consolidate identities | Duplicate supplier | No |
| 08 | Spelling variations | Both | Warning | Human Review Required | Acceptable | Master-data review | Potential duplicate | No |
| 09 | Zero price | Both | Fail | Blocked | Insufficient | Block calculation | Invalid price | Yes |
| 10 | Negative price | Both | Fail | Blocked | Insufficient | Block calculation | Invalid price | Yes |
| 11 | Extreme price | Both | Warning | Human Review Required | Acceptable | Outlier review | Price outlier | No |
| 12 | Lowest price / highest risk | Both | Pass | Eligible With Conditions | Acceptable | Best-value may reject lowest price | Trade-off | No |
| 13 | Highest price / best performance | Both | Pass | Eligible With Conditions | Acceptable | Explain cost-performance trade-off | Trade-off | No |
| 14 | Mixed currencies | Both | Fail | Blocked | Acceptable | No recommendation | FX normalization required | Yes |
| 15 | Missing currency | Both | Warning | Human Review Required | Limited | Provisional only | Confirm currency | No |
| 16 | Invalid FX rate | Both | Fail | Blocked | Any | Block conversion | Invalid FX | Yes |
| 17 | 0.95 vs 95 percent | Both | Warning | Human Review Required | Acceptable | Confirm convention | Percentage format | No |
| 18 | Annual volume zero | Both | Fail | Blocked | Any | No recommendation | Invalid demand | Yes |
| 19 | Total capacity below demand | Both | Fail | Blocked | Acceptable | No feasible allocation | Capacity shortfall | Yes |
| 20 | Primary capacity below allocation | Both | Fail | Blocked | Acceptable | Reallocate | Capacity exceedance | Yes |
| 21 | Backup capacity zero | Both | Fail/Warning | Human Review Required | Acceptable | Single-source mitigation | Backup infeasible | Conditional |
| 22 | Utilization above 100% | Both | Fail | Blocked | Insufficient | Block calculation | Invalid utilization | Yes |
| 23 | Allocation exceeds capacity | Both | Fail | Blocked | Acceptable | Recalculate | Capacity exceedance | Yes |
| 24 | Allocation not 100% | Both | Fail | Blocked | Any | Recalculate | Allocation total | Yes |
| 25 | One supplier / dual-source rule | Both | Fail | Human Review Required | Acceptable | Force single-source path | Logic contradiction | Yes if unresolved |
| 26 | MOQ above annual demand | Both | Warning | Human Review Required | Acceptable | Review inventory and commercial fit | Excess MOQ | No |
| 27 | High OTIF / high complaints | Both | Warning | Human Review Required | Acceptable | Investigate contradiction | Service-quality conflict | No |
| 28 | Low PPM / failed audit | Both | Warning | Human Review Required | Acceptable | Audit overrides comfort | Evidence conflict | No |
| 29 | High audit / poor delivery | Both | Warning | Eligible With Conditions | Acceptable | Development plan | Delivery weakness | No |
| 30 | Long lead / high service | Both | Warning | Eligible With Conditions | Acceptable | Explain resilience need | Lead-time risk | No |
| 31 | Missing quality data | Both | Warning | Human Review Required | Limited | Provisional | Quality evidence missing | No |
| 32 | Negative PPM/complaints | Both | Fail | Blocked | Insufficient | Block calculation | Invalid quality data | Yes |
| 33 | OTIF above 100% | Both | Fail | Blocked | Insufficient | Block calculation | Invalid percentage | Yes |
| 34 | Missing all financial data | Supplier 360 | Warning | Human Review Required | Limited | Indicator only | Due diligence required | No |
| 35 | Advance payment / high utilization | Both | Warning | Human Review Required | Acceptable | Financial mitigation | Working-capital stress | No |
| 36 | High buyer dependency | Supplier 360 | Warning | Human Review Required | Acceptable | Dependency mitigation | Financial signal | No |
| 37 | Supplier 360 mostly defaults | Supplier 360 | Warning | Insufficient Data | Insufficient | No final relationship status | Defaults dominate | Yes for final status |
| 38 | Strategic with weak risk | Supplier 360 | Fail | Human Review Required | Any | Downgrade or exception | Classification conflict | Yes if unresolved |
| 39 | Exit and Best Long-Term | Supplier 360 | Fail | Blocked | Any | Remove contradiction | Conflicting outputs | Yes |
| 40 | Missing ESG/innovation | Supplier 360 | Warning | Human Review Required | Limited | Provisional maturity only | Evidence missing | No |
| 41 | Price +100% | Both | Pass | Eligible With Conditions | Any | Recompute ranking | Severe scenario | No |
| 42 | Freight +200% | Both | Pass | Eligible With Conditions | Any | Recompute TCO | Severe scenario | No |
| 43 | Capacity -80% | Both | Fail if demand unmet | Blocked | Any | No infeasible allocation | Capacity shock | Yes if unmet |
| 44 | Lead time doubles | Both | Pass/Warning | Eligible With Conditions | Any | Recompute service/risk | Lead-time shock | No |
| 45 | Major currency depreciation | Raw material | Pass if normalized | Eligible With Conditions | Any | Recompute TCO | FX scenario | No |
| 46 | Commodity index below zero | Raw material | Fail | Blocked | Insufficient | Block calculation | Invalid index | Yes |
| 47 | Demand exceeds all capacity | Both | Fail | Blocked | Any | No award allocation | Demand shortfall | Yes |
| 48 | Multiple shocks | Both | Pass or Fail by feasibility | Human Review Required | Any | Provisional scenario output | Compound stress | Conditional |
