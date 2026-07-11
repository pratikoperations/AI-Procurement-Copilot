# Input–Output Traceability

| Input group | Primary fields | Processing modules | Outputs | Safety controls |
|---|---|---|---|---|
| RFQ identity | Supplier, category, commodity, plant | intelligent_rfq, category_engine | Canonical supplier records | Required-field and duplicate checks |
| Commercial | Quote, currency, UOM, MOQ, payment, incoterm | tco, raw_material_tco, scoring | TCO, commercial score, negotiation target | Positive price, currency/UOM consistency, data confidence |
| Demand and capacity | Annual volume, supplier capacity, utilization, capacity buffer | allocation, allocation_optimizer, business_rule_validator | Recommended allocation, capacity warnings | Capacity sufficiency and allocation feasibility gates |
| Service and quality | OTIF, PPM, audit, complaints, lead time | risk, raw_material_risk, supplier_performance_engine | Risk, performance, development actions | Range validation and contradiction warnings |
| Packaging cost | Substrate, film/resin, conversion, printing, scrap, tooling, freight | should_cost, tco | Packaging should-cost and TCO | Positive component and annualization checks |
| Raw-material cost | Commodity index, premium, duty, freight, FX, volatility | raw_material_cost, raw_material_tco | Raw-material should-cost and TCO | Positive index/cost and category-routing checks |
| ESG | Recyclability, PCR, carbon, certification, EPR, labor, governance | esg, supplier_esg_intelligence | ESG score and maturity | 0–100 checks, evidence disclaimer |
| Financial indicators | Capacity utilization, buyer dependency, revenue concentration, payment stress | supplier_financial_engine | Stability indicator, risk category, due diligence | Explicit non-audited disclaimer |
| Innovation | Design, material, automation, digital, AI readiness, CI | supplier_innovation_engine | Innovation score and agenda | Default tracking and confidence penalty |
| Relationship | Spend, criticality, switching, concentration, risk and performance | srm_engine, supplier360_engine | SRM class, governance cadence, Supplier 360 | Contradictory-classification checks |
| Decision | Total scores, strategy, risk, allocation, scenario | decision_engine, strategy_engine, recommendation_engine | Supplier recommendation and narrative | Eligibility gate and safe narrative withholding |
| Data quality | Missing, defaulted, inferred and supplied fields | data_confidence, validation_assurance | Data-confidence score and category | Explicit completeness meaning; not correctness probability |

## Traceability requirement

Every executive recommendation must be traceable back to supplier inputs, assumptions, formula or decision rule, validation status, and human approval requirement.
