# Architecture

## Architecture Principle

AI Procurement Copilot is a modular, category-aware procurement and supplier decision platform, not merely a Streamlit script.

## High-Level Layers

```text
AI Procurement Copilot
├── Presentation Layer
├── Category Engine Router
│   ├── Packaging Engine
│   └── Raw Material Engine
├── Intelligent RFQ Engine
├── Category-Specific Cost / Risk / TCO
├── Procurement Intelligence Engine
├── Supplier Intelligence Platform
├── Explainability and Executive Outputs
├── Validation, Tests, and CI
├── Export and Handoff Layer
└── Documentation and Recovery Layer
```

## Presentation Layer

Streamlit exposes category, commodity, RFQ, currency, scenario, allocation, Procurement Intelligence, and Supplier Intelligence workflows while keeping assumptions and maturity visible.

## Category Engine Router

`modules/category_engine.py` registers categories, routes requests, returns a governed profile contract, and prevents unsupported categories from failing silently.

## Category Engines

### Packaging Procurement — Active

Uses packaging-specific should-cost, TCO, risk, ESG, service, MOQ, lead-time, payment, incoterm, and continuity logic.

### Raw Material Procurement — Active

Uses commodity index, producer premium, freight, duty, FX, inventory, working capital, volatility, import dependency, concentration, substitution, capacity, quality, and continuity logic.

Supported raw materials:

- PET Resin
- Polyethylene
- Polypropylene
- Aluminium Foil
- Steel
- Copper

## Intelligent RFQ Engine

Normalizes CSV/Excel supplier files through exact and fuzzy header mapping, unit normalization, duplicate checks, numeric diagnostics, quality scoring, and blocking validation.

## Procurement Intelligence Engine

Includes:

- Executive decision engine
- Sourcing strategy engine
- Supplier allocation optimizer
- Negotiation intelligence
- Procurement risk intelligence
- Scenario simulation
- AI Explainability 2.0
- Executive decision narrative

## Supplier Intelligence Platform

### Supplier 360

`modules/supplier360_engine.py` combines supplier profile, capacity, qualification, performance, financial, ESG, innovation, and relationship outputs. Missing inputs are transparently defaulted and listed.

### Performance

`modules/supplier_performance_engine.py` evaluates quality, delivery, service, commercial competitiveness, corrective action, continuous improvement, capacity reliability, and innovation contribution.

### Financial Health

`modules/supplier_financial_engine.py` generates financial health indicators from available utilization, dependency, payment, and completeness signals. It does not claim audited financial facts or bankruptcy probability.

### ESG and Innovation

`modules/supplier_esg_intelligence.py` and `modules/supplier_innovation_engine.py` generate maturity scores, strengths, gaps, documentation needs, corrective actions, and collaboration opportunities.

### SRM

`modules/srm_engine.py` classifies suppliers as Strategic, Preferred, Approved, Transactional, Development, or Exit Candidate and assigns governance cadence and relationship strategy.

### Recommendation and Comparison

`modules/supplier_recommendation_engine.py` and `modules/supplier_comparison.py` produce deterministic rankings, side-by-side comparison, and executive supplier narrative.

## AI Assistance Layer

AI-style outputs support explanation, summarization, email drafting, negotiation playbooks, executive narratives, and interview communication. Decision logic remains rule-guided and auditable.

## Data Layer

Current sources:

- Synthetic packaging and raw-material demo data
- CSV RFQ upload
- Excel RFQ upload

Future production sources:

- Supplier master
- ERP and spend data
- QMS and OTIF history
- Audit and certification records
- Contract data
- Commodity indices
- Verified financial and country-risk data

## Governance Priorities

1. Explainability
2. Procurement credibility
3. Category separation
4. Transparent defaulting
5. Human approval
6. Modular code
7. Testability and CI
8. GitHub recoverability
9. Interview readiness
10. Future integration extensibility
