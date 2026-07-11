# AI Procurement Copilot

**Edition:** Portfolio Edition v1.0  
**Current Build:** Build 0.9.5 — Supplier Intelligence Platform  
**Status:** CI and Live Supplier Intelligence Validation Pending  
**Repository Owner:** pratikoperations

## Objective

AI Procurement Copilot is an interview-ready procurement decision intelligence project demonstrating strategic sourcing, category-specific should-cost, TCO optimization, supplier risk, Supplier 360, SRM, ESG, innovation, negotiation, allocation, scenario analysis, explainability, and executive recommendation capability.

## Build Philosophy

This is not a black-box AI award tool. Business rules, assumptions, category logic, scoring, defaults, and recommendations remain visible and auditable.

## Implemented Capabilities

- Synthetic demo data and CSV/Excel RFQ upload
- Intelligent RFQ header recognition, canonical mapping, unit normalization, and quality diagnostics
- Active Packaging Procurement and Raw Material Procurement engines
- Packaging-specific should-cost, TCO, and supplier risk
- Raw-material commodity-index should-cost, duty, freight, FX, inventory, working capital, volatility, and risk-adjusted TCO
- Category-specific scoring weights and decision routing
- Executive decision, sourcing strategy, allocation, negotiation, risk, and scenario intelligence
- Supplier 360 profiles with transparent default tracking
- Extended supplier performance intelligence
- Financial health indicators with due-diligence safeguards
- ESG and innovation maturity intelligence
- SRM classification and governance recommendations
- Explainable supplier recommendation rankings
- Side-by-side supplier comparison
- Executive supplier narrative
- AI Explainability 2.0
- Downloadable Excel, CSV, TXT, and JSON decision packages
- Automated regression tests, CI, and Streamlit smoke testing

## Supported Raw Materials

- PET Resin
- Polyethylene
- Polypropylene
- Aluminium Foil
- Steel
- Copper

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Run Tests

```bash
python -m pytest
```

## Input

Use built-in packaging or raw-material demo data, or upload a CSV/Excel RFQ. The Intelligent RFQ Engine recognizes common alternatives such as Vendor Name, Unit Rate, Minimum Order Quantity, Delivery Days, Credit Terms, Delivery Terms, and UOM.

## Output

The application generates:

- Category-specific should-cost and TCO
- Best-value supplier recommendation
- Sourcing strategy and optimized allocation
- Negotiation and risk intelligence
- Scenario-adjusted recommendation
- Supplier 360 profiles
- SRM classification
- Financial, ESG, innovation, and performance intelligence
- Supplier comparison and recommendation rankings
- Executive sourcing and supplier narratives
- Downloadable decision packages

## Architecture

```text
AI Procurement Copilot
├── Streamlit Presentation Layer
├── Category Engine Router
│   ├── Packaging Cost / Risk / TCO
│   └── Raw Material Cost / Risk / TCO
├── Intelligent RFQ Engine
├── Category-Aware Scoring Layer
├── Procurement Intelligence Engine
├── Supplier Intelligence Platform
│   ├── Supplier 360
│   ├── Performance
│   ├── Financial Health
│   ├── ESG
│   ├── Innovation
│   ├── SRM
│   ├── Recommendation Rankings
│   └── Supplier Comparison
├── Explainability and Executive Outputs
├── Validation, Tests, and CI
└── Export and Recovery Layer
```

## Documentation

- `PROJECT_STATUS.md`
- `ARCHITECTURE.md`
- `QUALITY_ASSURANCE_PROTOCOL.md`
- `docs/CATEGORY_ENGINE.md`
- `docs/INTELLIGENT_RFQ_ENGINE.md`
- `docs/PROCUREMENT_INTELLIGENCE_ENGINE.md`
- `docs/CATEGORY_SPECIFIC_COST_AND_RISK.md`
- `docs/SUPPLIER_INTELLIGENCE_PLATFORM.md`
- `docs/BUILD_0.9.5_QA_REPORT.md`
- `docs/USER_GUIDE.md`
- `docs/PORTFOLIO_ASSETS.md`
- `docs/DEMO_SCRIPT.md`

## Data and Governance Limits

- Defaulted fields are explicitly listed.
- Financial health outputs are indicators, not audited facts.
- Supplier recommendations do not replace legal, quality, commercial, risk, or executive approval.
- Historical intelligence improves when connected to ERP, QMS, SRM, audit, and financial data.

## Version Strategy

Build 0.9.5 is the feature-complete candidate for Portfolio Edition v1.0 release preparation. Future work should prioritize release hardening, UX polish, verified data integrations, and deeper category libraries rather than adding ungoverned feature breadth.

## Operating Standard

GitHub is the canonical source of truth. Every meaningful milestone updates project status, changelog, build history, version manifest, QA report, and recovery documentation.
