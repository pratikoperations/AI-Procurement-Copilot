# Architecture

## Architecture Principle

AI Procurement Copilot is a modular, category-aware procurement and supplier decision-support platform with explicit currency, unit, evidence-quality, validation, export, and human-approval governance.

## High-Level Layers

```text
AI Procurement Copilot
├── Streamlit Presentation Layer
├── Executive UI Component Layer
├── Category Engine Router
│   ├── Packaging Engine
│   └── Raw Material Engine
├── Intelligent RFQ Engine
├── Currency and Unit Governance
├── Category-Specific Cost / Risk / TCO
├── Procurement Intelligence Engine
├── Supplier Intelligence Platform
├── Evidence-Governed Recommendation Layer
├── Validation Assurance Layer
├── Category-Aware Communication Layer
├── Business-Readable Export Layer
├── Machine-Readable Audit Layer
├── Tests, CI and Validation Assets
└── Documentation and Recovery Layer
```

## Currency and Unit Governance

`modules/currency_unit_governance.py` preserves Original Currency and Original Unit Price, creates Normalized Currency and Normalized Unit Price, records FX Rate Used, and defines Unit of Measure and Comparison Basis. Unsupported currency conversion is blocked rather than silently assumed.

PET Resin uses kg in the current portfolio edition. Packaging uses piece where appropriate.

## Category Engines

### Packaging Procurement

Uses packaging-specific should-cost, TCO, risk, MOQ, service, payment, incoterm, quality, recyclability, PCR, EPR and continuity logic.

### Raw Material Procurement

Uses commodity index, producer premium, freight, duty, FX, inventory, working capital, volatility, import dependency, concentration, substitution, capacity, quality and continuity logic.

## Supplier Intelligence and Evidence Governance

Financial, ESG and Innovation outputs use governed displayed scores. Recommendation roles use those displayed scores and evidence status, not raw indicators alone.

The engine may return `No Qualified Supplier` for Most Innovative, Most Sustainable, Best Strategic Partner or Best Long-Term Supplier when evidence or governance conditions are insufficient.

Exit Candidate precedence prevents the same supplier from simultaneously receiving Development Candidate, Best Strategic Partner or Best Long-Term Supplier roles.

## Validation Assurance

- Data confidence measures supplied, defaulted, missing-critical and inferred data.
- Business rules validate price, volume, percentage, currency, UOM, capacity and allocation.
- Recommendation eligibility returns Eligible, Eligible With Conditions, Human Review Required, Insufficient Data or Blocked.
- Safe executive outputs withhold final-award language when validation fails.

## Category-Aware Communication

Supplier emails and executive memos are generated using category, commodity, unit and eligibility status. Packaging and Raw Material communications use different commercial topics. PET Resin communication uses kg and resin-specific terminology.

## Export Architecture

### Business-readable

- Supplier Scores Report
- Supplier Comparison Report
- Excel Analysis
- Executive Sourcing Memo
- Supplier Clarification Email
- Executive Supplier Narrative
- Supplier 360 Readable Report

### Machine-readable audit

- Decision audit data
- Supplier 360 audit data
- Raw supplier-score audit sheet inside Excel

Readable exports use business headings and governed scores. Audit outputs may retain technical fields for traceability.

## Governance Priorities

1. Recommendation safety
2. Currency and unit integrity
3. Evidence integrity
4. Cross-output consistency
5. Allocation feasibility
6. Explainability
7. Category separation
8. Executive readability
9. Human approval
10. GitHub recoverability

## Release Rule

Portfolio Edition v1.0 is not approved until Build 1.0 RC1.2 CI, Streamlit smoke testing, manual download inspection, defect closure, and independent review or formal waiver are complete.
