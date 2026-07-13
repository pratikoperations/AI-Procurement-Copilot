# Data Dictionary

## Governance

This dictionary is derived from the current v1.0.0 implementation. `modules/intelligent_rfq.py`, validation code, normalization code, and tests remain authoritative. Unknown fields are preserved where possible; unsupported values must not be silently invented.

## Canonical RFQ Fields

| Canonical field | Accepted aliases | Type | Status | Allowed/default behaviour | Validation / normalization | Consuming modules | Key outputs |
|---|---|---|---|---|---|---|---|
| `Supplier` | supplier, supplier name, vendor, vendor name, bidder, source | string | Mandatory for traceability | No fabricated default | Duplicate supplier names are diagnosed | data loader, validation, scoring, comparison, exports | Supplier identity in all reports |
| `Quoted Unit Price USD` | quoted unit price usd, unit price, quoted price, price, rate, unit rate, price usd, quoted rate, landed price | numeric | Mandatory commercial field | No safe fabricated price | Numeric conversion; later currency governance validates basis | currency governance, TCO, scoring | Original/normalized price, TCO |
| `MOQ` | moq, minimum order quantity, minimum qty, min order qty, order minimum | numeric | Required for governed calculations | Downstream packaging defaults 10,000; raw-material defaults 1,000 only where code explicitly applies them | Numeric conversion; positive-value safeguards | risk, TCO, scoring, allocation | MOQ and MOQ score |
| `Lead Time Days` | lead time days, lead time, delivery lead time, delivery days, lead days | numeric | Required for governed calculations | Downstream fallback 30 days | Numeric conversion | risk, TCO, scoring | Lead-time score, buffers, risk |
| `Payment Terms` | payment terms, payment term, credit terms, credit days, terms of payment | string | Required for commercial logic | Unparseable terms default to 30 days; advance without percentage is treated as 100% advance | Parsed by payment helpers | risk, TCO, scoring | Payment score, working capital, risk |
| `Incoterms` | incoterms, incoterm, delivery terms, shipping terms, trade terms | string | Required for freight logic | Recognized: DDP, DAP, CIF, FOB, EXW; otherwise `UNKNOWN` | Normalized by substring match | risk, packaging/raw-material TCO | Freight exposure, incoterm risk |
| `OTIF %` | otif %, otif, on time in full, on-time delivery, service level | numeric | Optional evidence; used in scores | Performance/risk fallback 90 | Numeric conversion | risk, performance | Service risk, performance score |
| `Quality PPM` | quality ppm, ppm, defect ppm, rejection ppm, quality defects | numeric | Optional evidence; used in scores | Performance/risk fallback 1,000 | Numeric conversion | risk, performance | Quality risk, performance score |
| `Audit Score` | audit score, supplier audit, quality audit score, audit rating | numeric | Optional evidence | Fallback 80 | Numeric conversion | performance | Performance score |
| `Complaint Rate %` | complaint rate %, complaint rate, complaints %, customer complaint rate | numeric | Optional evidence | Fallback 2.0 | Numeric conversion | performance | Performance score |
| `Capacity Buffer %` | capacity buffer %, capacity buffer, spare capacity %, available capacity % | numeric | Optional evidence | Fallback 10 | Numeric conversion | performance, risk intelligence | Performance/capacity outputs |
| `Recyclability` | recyclability, recyclability score, recyclable % | numeric | Optional ESG evidence | Fallback 75 | Numeric conversion | ESG | ESG score |
| `Certification` | certification, certification score, certifications, compliance score | numeric | Optional ESG evidence | Fallback 75 | Numeric conversion | ESG | ESG score |
| `Carbon Score` | carbon score, carbon rating, emission score, co2 score | numeric | Optional ESG evidence | Fallback 70 | Numeric conversion | ESG | ESG score |
| `EPR Readiness` | epr readiness, epr score, epr compliance | numeric | Optional ESG evidence | Fallback 70 | Numeric conversion | ESG | ESG score |
| `PCR Content %` | pcr content %, pcr content, recycled content %, post consumer recycled % | numeric | Optional ESG evidence | Fallback 0; converted to score at 2× and capped at 100 | Numeric conversion | ESG | ESG score |
| `Supplier Capacity` | supplier capacity, capacity, annual capacity, available volume | numeric | Raw-material / allocation evidence | No universal default at ingestion | Numeric conversion | allocation, risk intelligence | Capacity constraint / diagnostics |
| `Currency` | currency, currency code, quote currency | string | Mandatory for non-USD governance | No invented FX rate | Currency governance preserves original and normalizes only supported cases | currency governance, exports | Original/normalized currency, FX rate |
| `Unit` | unit, uom, unit of measure, measurement unit | string | Mandatory comparison basis | Unknown values preserved | Aliases: kg/kgs/kilogram(s)→kg; mt/ton(s)/tonne(s)→MT; pc/pcs/piece(s)/ea→piece; m/meter(s)/metre(s)→meter; l/ltr/litre/liter(s)→liter | unit governance, TCO, exports | Unit of Measure, Comparison Basis |
| `Material` | material, commodity, item, product, grade | string | Category context | No fabricated default in upload normalization | Header mapping only | category engine, UI | Commodity/material labels |
| `Plant` | plant, location, site, supplier location | string | Optional context | No default | Header mapping only | comparison / reporting where present | Location context |

## Additional Implemented Inputs

| Field | Type | Default / allowed behaviour | Authority | Output effect |
|---|---|---|---|---|
| `Embedded Freight Share` | numeric ratio | 0.02 | `modules/tco.py`, `modules/raw_material_tco.py` | Delivered-price freight shock |
| `Duty %` | numeric percent | 0 | `modules/raw_material_tco.py` | Duty cost |
| `Commodity Volatility %` | numeric percent | 15 | `modules/raw_material_tco.py` | Volatility buffer |
| `Import Dependency %`, `Supplier Concentration %`, `Substitute Available` | numeric/string | See raw-material risk implementation | `modules/raw_material_risk.py` | Raw-material risk score |

## Derived Fields

| Field | Type / basis | Produced by | Used in / exported as |
|---|---|---|---|
| `scenario_unit_price_usd`, `freight_cost_usd`, `inventory_cost_usd`, `working_capital_impact_usd`, `risk_penalty_usd`, `lead_time_buffer_usd`, `duty_cost_usd`, `volatility_buffer_usd` | numeric USD per governed unit | TCO engines | TCO breakdown, scenarios, audit outputs |
| `adjusted_tco_unit_usd`, `annual_tco_usd` | numeric USD | TCO engines | Scoring, decision, dashboards, exports |
| `risk_score`, `risk_category` | 0–100 and label | Risk engines | Visible as Risk Resilience Score / category |
| `performance_score`, `esg_score`, `tco_score`, `moq_score`, `lead_time_score`, `payment_score`, `total_score` | 0–100 | Scoring modules | Supplier ranking and reports |
| Original/normalized currency, unit, FX rate and comparison basis fields | labelled business fields | currency/unit governance and export builders | Readable supplier reports and Excel |
| Data confidence, eligibility, validation warning and human review fields | governance outputs | validation assurance | UI, communications, readable/audit exports |

## Header Recognition and Missing Values

- Exact cleaned aliases map with confidence 1.0; fuzzy mappings require a similarity score of at least 0.72.
- A second source column targeting an already mapped canonical field is not remapped.
- Listed numeric fields are converted with invalid values becoming blank and being reported.
- Mandatory commercial or normalization gaps block or make the relevant workflow ineligible.
- Optional evidence gaps may retain the supplier with reduced confidence, capped conclusions and disclosure.
- Defaults apply only where explicitly coded and listed above; they must not be interpreted as verified supplier facts.
- Sensitive or supplier-confidential data must not be committed to the public portfolio repository.