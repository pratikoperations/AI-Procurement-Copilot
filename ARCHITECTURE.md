# Architecture

## Architecture Principle

AI Procurement Copilot is a modular, category-aware procurement and supplier decision-support platform with explicit safety, data-confidence, evidence-quality and human-approval gates.

## High-Level Layers

```text
AI Procurement Copilot
├── Streamlit Presentation Layer
├── Executive UI Component Layer
├── Category Engine Router
│   ├── Packaging Engine
│   └── Raw Material Engine
├── Intelligent RFQ Engine
├── Category-Specific Cost / Risk / TCO
├── Procurement Intelligence Engine
├── Supplier Intelligence Platform
├── Evidence Governance Layer
│   ├── Financial Completeness
│   ├── ESG Completeness
│   └── Innovation Completeness
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

Streamlit exposes category, commodity, RFQ, scenario, allocation, Procurement Intelligence, Supplier Intelligence and Validation Assurance workflows. Synthetic data is distinguished from uploaded unverified data.

`modules/ui_components.py` provides reusable cards, status indicators, score bars, matrices, evidence lists, action plans, risk alerts, governance notes and responsive charts. Raw structured payloads are not rendered in the interface.

## Category Engines

### Packaging Procurement — Active

Uses packaging-specific should-cost, TCO, risk, ESG, service, MOQ, lead-time, payment, incoterm and continuity logic.

### Raw Material Procurement — Active

Uses commodity index, producer premium, freight, duty, FX, inventory, working capital, volatility, import dependency, concentration, substitution, capacity, quality and continuity logic.

## Intelligent RFQ Engine

Normalizes supplier files through header mapping, unit normalization, duplicate checks, numeric diagnostics, quality scoring and blocking validation.

## Procurement Intelligence Engine

Includes executive decision, strategy, allocation, negotiation, risk, scenarios, explainability and executive narrative.

## Supplier Intelligence Platform

Includes Supplier 360, performance, financial indicators, ESG maturity, innovation maturity, SRM classification, supplier comparison and explainable recommendation rankings.

## Evidence Governance Layer

### Financial

Low-completeness financial data cannot produce a verified strong conclusion. The displayed score is capped, assessment status is explicit and due diligence is mandatory when evidence is weak.

### ESG

ESG completeness governs the displayed score and maturity ceiling. Insufficient evidence cannot produce Leading or Advanced maturity.

### Innovation

Innovation completeness governs the displayed score and maturity ceiling. Insufficient evidence cannot produce a maturity above Basic.

Raw indicator scores remain available internally for auditability, while displayed scores reflect evidence quality.

## Validation Assurance Layer

- `modules/data_confidence.py` measures supplied, defaulted, missing-critical and inferred data.
- `modules/business_rule_validator.py` validates price, volume, percentages, currency, UOM, capacity, allocation and contradictory statuses.
- `modules/recommendation_eligibility.py` returns Eligible, Eligible With Conditions, Human Review Required, Insufficient Data or Blocked.
- `modules/validation_assurance.py` withholds polished final-award language when validation does not permit it.

## Export Layer

Readable reports, CSV and Excel files support business review. Machine-readable audit data remains download-only and is not displayed on-screen.

## Validation Assets

- Formula and assumption registers
- Decision-rule and input-output traceability
- Known model limitations
- Expected-result matrix
- Defect register
- Release-readiness scorecard
- Model-risk statement
- Synthetic file cases
- Adversarial and external-file tests
- UI-output and evidence-governance tests
- Gemini, Perplexity and human-review templates

## Governance Priorities

1. Recommendation safety
2. Evidence integrity
3. Allocation feasibility
4. Explainability
5. Procurement credibility
6. Executive readability
7. Category separation
8. Human approval
9. Testability and independent validation
10. GitHub recoverability

## Release Rule

Portfolio Edition v1.0 is not approved until Build 0.9.6.1 CI and live validation pass, independent AI reviews and human review are completed or formally waived, defects are closed and final release-readiness evidence is approved.
