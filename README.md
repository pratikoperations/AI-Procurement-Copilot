# AI Procurement Copilot

**Edition:** Portfolio Edition v1.0  
**Current Build:** Build 0.8.1 — Deployment Stabilization  
**Status:** Streamlit Cloud Redeployment Validation Pending  
**Repository Owner:** pratikoperations

## Objective

AI Procurement Copilot is an interview-ready procurement decision intelligence project demonstrating senior-level procurement transformation, packaging sourcing, explainable AI, RFQ analysis, should-cost modeling, TCO optimization, supplier risk assessment, ESG evaluation, negotiation planning, and executive sourcing recommendation capability.

## Build Philosophy

This is not a black-box AI award tool. It is a transparent, rule-guided, AI-ready procurement decision platform where business rules, assumptions, scoring logic, and recommendations remain visible and auditable.

## Implemented Capabilities

- Synthetic demo data and CSV/Excel RFQ upload
- RFQ validation
- Packaging should-cost engine
- Risk-adjusted TCO model
- Structured supplier risk model
- ESG and supplier performance scoring
- Lowest-price vs best-value decision
- Scenario stress testing
- Supplier allocation recommendation
- Negotiation simulator and playbook
- Executive sourcing memo
- Supplier clarification email
- AI-style explainability panel
- Interview talking points
- Core and export regression tests
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

Use the built-in synthetic demo or upload a CSV/Excel RFQ. A sample file is available at:

`sample_data/sample_packaging_rfq.csv`

## Output

The app generates a transparent best-value sourcing recommendation, should-cost build-up, TCO analysis, risk/ESG/performance scores, allocation recommendation, scenario results, negotiation strategy, executive memo, supplier email, interview explanation, and downloadable decision package.

## High-Level Architecture

```text
AI Procurement Copilot
├── Presentation Layer: Streamlit
├── Procurement Decision Engine
├── Category Engine: Packaging v1.0
├── Future Category Engine: Raw Materials v1.1
├── Business Rules Layer
├── AI Assistance Layer
├── Data Validation + Test Layer
├── Export + Handoff Layer
└── Documentation + Recovery Layer
```

## Documentation

- `PROJECT_STATUS.md`
- `PROJECT_BUILD_PLAN.md`
- `ARCHITECTURE.md`
- `QUALITY_ASSURANCE_PROTOCOL.md`
- `docs/USER_GUIDE.md`
- `docs/BASE_BUILD_PLAN_REFERENCE.md`
- `docs/RELEASE_CANDIDATE_CHECKLIST.md`
- `docs/BUILD_0.8_QA_REPORT.md`
- `docs/BUILD_0.8.1_QA_REPORT.md`
- `docs/PORTFOLIO_ASSETS.md`
- `docs/DEMO_SCRIPT.md`
- `assets/screenshots/README.md`

## Version Strategy

- **v1.0:** Packaging Procurement Engine
- **v1.1:** Raw Material Procurement Engine
- **v2.0:** Multi-category Procurement Platform

## Operating Standard

GitHub is the canonical source of truth. Every meaningful milestone must be committed with project status, changelog, build history, version manifest, and recovery documentation updated.
