# Architecture

## Architecture Principle

AI Procurement Copilot is a modular, category-aware procurement and supplier decision-support platform with explicit safety, data-confidence and human-approval gates.

## High-Level Layers

```text
AI Procurement Copilot
├── Streamlit Presentation Layer
├── Category Engine Router
│   ├── Packaging Engine
│   └── Raw Material Engine
├── Intelligent RFQ Engine
├── Category-Specific Cost / Risk / TCO
├── Procurement Intelligence Engine
├── Supplier Intelligence Platform
├── Validation Assurance Layer
│   ├── Data Confidence
│   ├── Business Rule Validator
│   ├── Recommendation Eligibility
│   └── Safe Executive Output
├── Explainability and Executive Outputs
├── Tests, CI and External Validation Assets
├── Export and Handoff Layer
└── Documentation and Recovery Layer
```

## Presentation Layer

Streamlit exposes category, commodity, RFQ, currency, scenario, allocation, Procurement Intelligence, Supplier Intelligence and Validation Assurance workflows. The interface distinguishes synthetic demonstration data from uploaded unverified supplier data.

## Category Engines

### Packaging Procurement — Active

Uses packaging-specific should-cost, TCO, risk, ESG, service, MOQ, lead-time, payment, incoterm and continuity logic.

### Raw Material Procurement — Active

Uses commodity index, producer premium, freight, duty, FX, inventory, working capital, volatility, import dependency, concentration, substitution, capacity, quality and continuity logic.

## Intelligent RFQ Engine

Normalizes supplier files through exact and fuzzy header mapping, unit normalization, duplicate checks, numeric diagnostics, quality scoring and blocking validation.

## Procurement Intelligence Engine

Includes executive decision, strategy, allocation, negotiation, risk, scenarios, explainability and executive narrative.

## Supplier Intelligence Platform

Includes Supplier 360, extended performance, financial-health indicators, ESG maturity, innovation maturity, SRM classification, supplier comparison and explainable recommendation rankings.

## Validation Assurance Layer

### Data confidence

`modules/data_confidence.py` measures supplied, defaulted, missing-critical and inferred data. The score measures completeness and reliability, not correctness probability.

### Business-rule validation

`modules/business_rule_validator.py` validates price, volume, percentages, currency, UOM, capacity, allocation and contradictory statuses.

### Recommendation eligibility

`modules/recommendation_eligibility.py` returns:

- Eligible
- Eligible With Conditions
- Human Review Required
- Insufficient Data
- Blocked

### Safe executive outputs

`modules/validation_assurance.py` orchestrates validation and withholds polished final-award language when validation does not permit it.

## Validation Assets

- Formula and assumption registers
- Decision-rule and input-output traceability
- Known model limitations
- Expected-result matrix
- Defect register
- Release-readiness scorecard
- Model-risk statement
- Fourteen synthetic file cases
- Adversarial and external-file tests
- Gemini, Perplexity and human-review templates

## Data Layer

Current sources:

- Synthetic packaging and raw-material demo data
- CSV RFQ upload
- Excel RFQ upload
- Synthetic validation datasets

Future production sources:

- Verified supplier master
- ERP and spend data
- QMS and OTIF history
- Audit, certification and ESG records
- Contract data
- Commodity indices and FX feeds
- Verified financial and country-risk data

## Governance Priorities

1. Recommendation safety
2. Allocation feasibility
3. Explainability
4. Procurement credibility
5. Category separation
6. Transparent defaulting
7. Human approval
8. Testability and independent validation
9. GitHub recoverability
10. Interview readiness

## Release Rule

Portfolio Edition v1.0 is not approved until CI, live deployment, independent AI reviews, human review or formal waiver, defect closure and final release-readiness evidence are complete.
