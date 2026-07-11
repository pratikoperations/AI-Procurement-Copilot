# AI Procurement Copilot

**Edition:** Portfolio Edition v1.0  
**Current Build:** Build 0.9.4 — Category-Specific Cost and Risk Engines  
**Status:** CI and Live Multi-Category Validation Pending  
**Repository Owner:** pratikoperations

## Objective

AI Procurement Copilot is an interview-ready procurement decision intelligence project demonstrating strategic sourcing, category-specific should-cost, TCO optimization, supplier risk, ESG, negotiation, allocation, scenario analysis, explainability, and executive recommendation capability.

## Build Philosophy

This is not a black-box AI award tool. Business rules, assumptions, category logic, scoring, and recommendations remain visible and auditable.

## Implemented Capabilities

- Synthetic demo data and CSV/Excel RFQ upload
- Intelligent RFQ header recognition, canonical mapping, unit normalization, and quality diagnostics
- Active Packaging Procurement and Raw Material Procurement engines
- Packaging-specific should-cost, TCO, and supplier risk
- Raw-material commodity-index should-cost
- Raw-material duty, freight, FX, inventory, working-capital, volatility, and risk-adjusted TCO
- Commodity volatility, import dependency, concentration, substitution, capacity, quality, currency, logistics, and commercial risk
- Category-specific scoring weights and decision routing
- ESG and supplier performance scoring
- Lowest-price versus best-value decision
- Executive decision, sourcing strategy, supplier allocation, negotiation intelligence, and risk intelligence
- Scenario simulation and recommendation recomputation
- AI Explainability 2.0 and board-ready decision narrative
- Executive memo and supplier clarification email
- Automated regression tests, CI, and Streamlit smoke testing
- Downloadable Excel, CSV, TXT, and JSON decision packages
- Public Streamlit deployment baseline on Python 3.11

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

Use built-in packaging or raw-material demo data, or upload a CSV/Excel RFQ. The Intelligent RFQ Engine recognizes common supplier-template alternatives such as Vendor Name, Unit Rate, Minimum Order Quantity, Delivery Days, Credit Terms, Delivery Terms, and UOM.

## Output

The application generates:

- Category-specific should-cost and TCO
- Best-value supplier recommendation
- Award confidence and rejected-supplier rationale
- Sourcing strategy and optimized allocation
- Negotiation priorities and savings opportunities
- Risk severity, evidence, and mitigation
- Scenario-adjusted recommendation
- Executive decision narrative
- Downloadable decision package

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
│   ├── Decision Engine
│   ├── Strategy Engine
│   ├── Allocation Optimizer
│   ├── Negotiation Intelligence
│   ├── Risk Intelligence
│   └── Scenario Engine
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
- `docs/BUILD_0.9.4_QA_REPORT.md`
- `docs/USER_GUIDE.md`
- `docs/PORTFOLIO_ASSETS.md`
- `docs/DEMO_SCRIPT.md`

## Version Strategy

The final Portfolio Edition v1.0 release scope will be frozen in Build 0.9.5 after multi-category validation. Future work remains planned for deeper category libraries and a broader multi-category platform.

## Operating Standard

GitHub is the canonical source of truth. Every meaningful milestone updates project status, changelog, build history, version manifest, QA report, and recovery documentation.
