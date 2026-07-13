# Formula Traceability Register

## Governance

This register documents formulas and decision rules verified directly from Portfolio Edition v1.0.0 source code. Executable code and tests remain authoritative. Any change requires explicit approval, targeted regression coverage, changelog documentation, and validation of affected exports and recommendations.

## Supplier Scoring

| Rule | Exact implementation | Purpose | Inputs / outputs | Units / basis | Defaults / thresholds | Missing-data behaviour | Authority | Tests / approval |
|---|---|---|---|---|---|---|---|---|
| Packaging total score | `tco_score*0.40 + risk_score*0.20 + lead_time_score*0.10 + payment_score*0.08 + moq_score*0.07 + performance_score*0.10 + esg_score*0.05` | Rank packaging suppliers by best value | Supplier metrics → `total_score` | 0–100 score | Weights sum to 1.00 | Upstream defaults and validation apply | `modules/scoring.py::enrich_supplier_scores`, `DEFAULT_WEIGHTS` | Relevant scoring, validation, scenario and export tests; procurement owner approval |
| Raw-material total score | `tco_score*0.38 + risk_score*0.27 + lead_time_score*0.08 + payment_score*0.07 + moq_score*0.05 + performance_score*0.10 + esg_score*0.05` | Increase risk emphasis for raw materials | Supplier metrics → `total_score` | 0–100 score | Weights sum to 1.00 | Upstream defaults and validation apply | `modules/scoring.py::enrich_supplier_scores`, `RAW_MATERIAL_WEIGHTS` | Same controls as above |
| Relative TCO score | `(minimum positive adjusted TCO / supplier adjusted TCO) * 100` | Reward lowest governed TCO | `adjusted_tco_unit_usd` → `tco_score` | Relative percentage | Positive-value safeguard | `safe_positive` prevents invalid denominators | `modules/scoring.py::enrich_supplier_scores` | Calculation regression required |
| Relative MOQ score | `(minimum positive MOQ / supplier MOQ) * 100` | Reward lower minimum order quantity | `MOQ` → `moq_score` | Relative percentage | Positive-value safeguard | Defaults originate in TCO/risk logic where absent | `modules/scoring.py::enrich_supplier_scores` | Calculation regression required |
| Relative lead-time score | `(minimum positive lead time / supplier lead time) * 100` | Reward shorter lead time | `Lead Time Days` → `lead_time_score` | Relative percentage | Positive-value safeguard | Default lead time is 30 days in downstream engines | `modules/scoring.py::enrich_supplier_scores` | Calculation regression required |
| Payment score | `min(extracted payment days, 90) / 90 * 100`; extraction fallback 30 | Reward longer credit terms | `Payment Terms` → `payment_score` | 0–100 score | Cap 90 days; fallback 30 | Missing/unparseable terms score as 30-day terms | `modules/scoring.py::enrich_supplier_scores` | Boundary tests required |

## Performance and ESG

| Rule | Exact implementation | Purpose | Inputs / outputs | Defaults / thresholds | Authority |
|---|---|---|---|---|---|
| Performance score | `OTIF*0.32 + max(100-PPM/30,0)*0.23 + Audit*0.23 + max(100-ComplaintRate*12,0)*0.12 + min(CapacityBuffer*4,100)*0.10` | Consolidate delivery, quality, audit, complaints and capacity | Inputs → `performance_score` | OTIF 90; PPM 1000; Audit 80; Complaint 2.0%; Capacity Buffer 10% | `modules/performance.py::calculate_performance_score` |
| ESG score | `Recyclability*0.30 + Certification*0.25 + Carbon*0.20 + EPR*0.20 + min(PCRContent*2,100)*0.05` | Consolidate sustainability indicators | Inputs → `esg_score` | Recyclability 75; Certification 75; Carbon 70; EPR 70; PCR 0 | `modules/esg.py::calculate_esg_score` |

## Packaging Risk and TCO

| Rule | Exact implementation / threshold | Purpose | Authority |
|---|---|---|---|
| Payment risk | 25 if any advance; otherwise 10 if payment days <30; else 0 | Commercial exposure | `modules/risk.py::calculate_risk` |
| Incoterm risk | EXW 25; FOB 15; CIF 7; otherwise 0 | Logistics exposure | `modules/risk.py::calculate_risk` |
| Lead-time risk | >45 days 20; >30 10; >21 5; else 0 | Continuity exposure | `modules/risk.py::calculate_risk` |
| MOQ risk | >200,000 15; >75,000 10; >50,000 8; else 0 | Inventory/commitment exposure | `modules/risk.py::calculate_risk` |
| Service risk | OTIF <85 →15; <90 →8; else 0 | Delivery exposure | `modules/risk.py::calculate_risk` |
| Quality risk | PPM >2,000 →20; >1,200 →10; >900 →5; else 0 | Quality exposure | `modules/risk.py::calculate_risk` |
| Risk resilience score | `normalize_score(100 - sum(risk penalties))`; Low Risk ≥75, Medium Risk ≥50, else High Risk | Produce visible risk capability score | `modules/risk.py::calculate_risk` |
| Packaging scenario price | `base_price * (0.60*(1+raw_material_shock)+0.40)` | Stress raw-material share | `modules/tco.py::calculate_supplier_tco` |
| Freight exposure | DDP 0; DAP 20%; CIF 35%; FOB 75%; EXW 100%; unknown 60% of maximum exposure. Maximum default 6%. During shock, delivered quotes use embedded share default 2% | Model incoterm and pass-through exposure | `modules/tco.py::freight_factor_for_incoterm`, `freight_cost_factor_for_scenario` |
| Inventory cost | `((MOQ/2 + effective_volume*(lead_days*0.5/365))*scenario_price*0.18)/effective_volume` | Carrying-cost impact | `modules/tco.py::calculate_supplier_tco` |
| Working-capital impact | `advance_cost - credit_benefit`, using 12% cost of capital and 60-day advance horizon | Payment-term economics | `modules/tco.py::calculate_supplier_tco` |
| Failure probability / penalty | `((100-risk_score)/100)*0.20`; penalty = `scenario_price*failure_probability*0.50` | Risk-adjust TCO | `modules/tco.py::calculate_supplier_tco` |
| Lead-time buffer | >45 days 1.5%; >30 0.75%; >21 0.3%; else 0 of scenario price | Continuity buffer | `modules/tco.py::calculate_supplier_tco` |
| Adjusted packaging TCO | Sum of scenario price, freight, inventory, working-capital impact, risk penalty and lead-time buffer; annual TCO = unit TCO × effective volume | Comparable annual economics | `modules/tco.py::calculate_supplier_tco` |

## Raw-Material TCO

| Rule | Exact implementation | Defaults / thresholds | Authority |
|---|---|---|---|
| Scenario price | `base_price*(1+commodity_shock)` | No shock by default | `modules/raw_material_tco.py::calculate_raw_material_tco` |
| Freight | Shared freight scenario logic with maximum exposure 8% and embedded share default 2% | Incoterm-based | Same function |
| Duty | `scenario_price*(Duty %/100)` | Duty default 0 | Same function |
| Inventory | `((MOQ/2 + effective_volume*(lead_days/365)*0.5)*scenario_price*0.18)/effective_volume` | MOQ 1,000; lead time 30; carrying rate 18% | Same function |
| Working capital | Same advance/credit method as packaging at 12% cost of capital | Payment terms default Net 30 | Same function |
| Failure risk | `((100-risk_score)/100)*0.25`; penalty = `scenario_price*failure_probability*0.65` | Fixed multipliers | Same function |
| Volatility buffer | `scenario_price*(Commodity Volatility %/100)*0.10` | Volatility default 15% | Same function |
| Adjusted raw-material TCO | Sum of scenario price, freight, duty, inventory, working capital, risk penalty and volatility buffer; annual TCO = unit TCO × effective volume | USD comparison basis after normalization | Same function |

## RFQ Recognition and Data Quality

| Rule | Exact implementation | Authority |
|---|---|---|
| Fuzzy header match | Exact cleaned alias match first; otherwise `SequenceMatcher` score ≥0.72 | `modules/intelligent_rfq.py::_best_column_match` |
| Duplicate-target control | Only first source column mapped to a canonical target; later duplicates remain unmapped | `modules/intelligent_rfq.py::detect_column_mapping` |
| Upload quality score | Mapping contributes 45%, completeness 55%; duplicate penalty `min(rows*0.05,0.25)` and conversion penalty `min(issue_count*0.03,0.20)` | `modules/intelligent_rfq.py::normalize_rfq_dataframe` |
| Numeric conversion | Invalid numeric values become blank and are counted in quality diagnostics | Same function |

## Change Approval

Any formula, weight, threshold, default, alias, normalization, eligibility or output-mapping change requires: procurement/business owner approval; targeted unit tests; full `python -m pytest`; Streamlit smoke test where relevant; direct export review where outputs change; changelog update; and rollback instructions.