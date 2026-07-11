# AI Procurement Copilot

**Edition:** Portfolio Edition v1.0  
**Current Build:** Build 0.9.3 — Procurement Intelligence Engine  
**Status:** CI and Live Dashboard Validation Pending  
**Repository Owner:** pratikoperations

## Objective

AI Procurement Copilot is an interview-ready procurement decision intelligence project demonstrating senior-level procurement transformation, packaging sourcing, explainable AI, RFQ analysis, should-cost modeling, TCO optimization, supplier risk assessment, ESG evaluation, negotiation planning, and executive sourcing recommendation capability.

## Build Philosophy

This is not a black-box AI award tool. It is a transparent, rule-guided, AI-ready procurement decision platform where business rules, assumptions, scoring logic, and recommendations remain visible and auditable.

## Implemented Capabilities

- Synthetic demo data and CSV/Excel RFQ upload
- Intelligent RFQ header recognition and canonical mapping
- Unit normalization and RFQ quality diagnostics
- Multi-category architecture with active Packaging Procurement and Raw Material foundation preview
- Packaging should-cost engine
- Risk-adjusted TCO model
- Structured supplier risk model
- ESG and supplier performance scoring
- Lowest-price vs best-value decision
- Deterministic executive decision engine
- Procurement strategy recommendation
- Supplier allocation optimizer
- Negotiation intelligence
- Procurement risk intelligence
- Scenario simulation and recommendation recomputation
- AI Explainability 2.0
- Board-ready executive decision narrative
- Executive sourcing memo and supplier clarification email
- Core, export, category, RFQ, and procurement-intelligence regression tests
- Automated Streamlit smoke testing
- Downloadable Excel, CSV, TXT, and JSON decision packages
- Resume, LinkedIn, demo-script, and screenshot portfolio assets
- Reproducible Python 3.11 deployment baseline

## Deployment Baseline

- Python 3.11 via `runtime.txt`
- Streamlit 1.59.1
- Pandas 2.2.3
- NumPy 2.1.3
- Plotly 5.24.1
- OpenPyXL 3.1.5

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

Use the built-in synthetic demo or upload a CSV/Excel RFQ. The Intelligent RFQ Engine recognizes common alternatives such as Vendor Name, Unit Rate, Minimum Order Quantity, Delivery Days, Credit Terms, Delivery Terms, and UOM.

Sample file:

`sample_data/sample_packaging_rfq.csv`

## Output

The app generates:

- Best-value supplier recommendation
- Award confidence
- Sourcing strategy
- Optimized allocation
- Negotiation priorities
- Risk severity and mitigation
- Scenario-adjusted recommendation
- Explainability and rejected-supplier rationale
- Executive decision narrative
- Downloadable decision package

## High-Level Architecture

```text
AI Procurement Copilot
├── Presentation Layer: Streamlit
├── Category Engine Router
├── Intelligent RFQ Engine
├── Procurement Scoring and TCO Layer
├── Procurement Intelligence Engine
│   ├── Decision Engine
│   ├── Strategy Engine
│   ├── Allocation Optimizer
│   ├── Negotiation Intelligence
│   ├── Risk Intelligence
│   └── Scenario Engine
├── Explainability and Executive Output Layer
├── Data Validation + Test Layer
├── Export + Handoff Layer
└── Documentation + Recovery Layer
```

## Documentation

- `PROJECT_STATUS.md`
- `PROJECT_BUILD_PLAN.md`
- `ARCHITECTURE.md`
- `QUALITY_ASSURANCE_PROTOCOL.md`
- `docs/CATEGORY_ENGINE.md`
- `docs/INTELLIGENT_RFQ_ENGINE.md`
- `docs/PROCUREMENT_INTELLIGENCE_ENGINE.md`
- `docs/BUILD_0.9.3_QA_REPORT.md`
- `docs/USER_GUIDE.md`
- `docs/BASE_BUILD_PLAN_REFERENCE.md`
- `docs/RELEASE_CANDIDATE_CHECKLIST.md`
- `docs/PORTFOLIO_ASSETS.md`
- `docs/DEMO_SCRIPT.md`
- `assets/screenshots/README.md`

## Version Strategy

- **v1.0:** Packaging Procurement Engine
- **v1.1:** Raw Material Procurement Engine
- **v2.0:** Multi-category Procurement Platform

## Operating Standard

GitHub is the canonical source of truth. Every meaningful milestone must be committed with project status, changelog, build history, version manifest, QA report, and recovery documentation updated.
