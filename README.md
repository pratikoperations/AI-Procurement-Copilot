# AI Procurement Copilot

**Edition:** Portfolio Edition v1.0  
**Current Build:** Build 0.7 — Release Candidate Preparation  
**Status:** Release Candidate Validation Pending  
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
- Automated regression test workflow
- Downloadable Excel, CSV, TXT, and JSON decision packages

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Run Tests

```bash
pytest -q
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

## Version Strategy

- **v1.0:** Packaging Procurement Engine
- **v1.1:** Raw Material Procurement Engine
- **v2.0:** Multi-category Procurement Platform

## Operating Standard

GitHub is the canonical source of truth. Every meaningful milestone must be committed with project status, changelog, build history, version manifest, and recovery documentation updated.
