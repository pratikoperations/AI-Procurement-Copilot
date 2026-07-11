# AI Procurement Copilot

**Edition:** Portfolio Edition v1.0  
**Current Build:** Build 0.9.6.1 — Executive-Readable Supplier Intelligence UX Hotfix  
**Status:** Hotfix Validation Pending  
**Repository Owner:** pratikoperations

## Objective

AI Procurement Copilot is an interview-ready procurement decision-support project covering category-specific should-cost, TCO, risk, Procurement Intelligence, Supplier 360, SRM, data-confidence governance, recommendation eligibility and executive communication.

## Build Philosophy

The platform is transparent, rule-guided and human-controlled. It is not a black-box supplier-award system. Inputs, assumptions, defaults, formulas, data gaps, validation failures and recommendation conditions remain visible and auditable.

## Implemented Capabilities

- Synthetic demo data and CSV/Excel RFQ upload
- Intelligent header recognition, canonical mapping and unit normalization
- Active Packaging Procurement and Raw Material Procurement engines
- Category-specific should-cost, TCO, risk and scoring
- Executive decision, strategy, allocation, negotiation, risk and scenario intelligence
- Supplier 360, performance, financial indicators, ESG, innovation and SRM classification
- Supplier comparison, recommendation rankings and executive narratives
- Executive-readable cards, score matrices, charts, evidence lists and action plans
- Data-confidence scoring
- Recommendation eligibility gate
- Business-rule validation
- Safe withholding of final-award language
- Financial, ESG and innovation evidence-completeness safeguards
- Synthetic real-world and adversarial validation datasets
- Regression tests, CI, Streamlit smoke testing and governance documentation

## Build 0.9.6.1 UX and Evidence Controls

Supplier Intelligence no longer renders raw structured payloads. Performance, Financial, ESG, Innovation and SRM outputs are displayed using readable business components.

Evidence rules:

- Financial completeness below 40% becomes Insufficient Data and the displayed indicator is capped at 50.
- ESG completeness below 40% becomes Insufficient Data and maturity cannot exceed Basic.
- Innovation completeness below 40% becomes Insufficient Data and maturity cannot exceed Basic.
- Limited evidence between 40% and 69% is capped at 70 and remains provisional.
- Machine-readable audit data remains download-only.

## Build 0.9.6 Safety Controls

The application checks required data, valid ranges, positive price and volume, currency and UOM consistency, capacity sufficiency, allocation feasibility, percentage conventions, missing/defaulted/inferred data and whether final-award language is permitted.

Eligibility states:

- Eligible
- Eligible With Conditions
- Human Review Required
- Insufficient Data
- Blocked

Data confidence measures completeness and reliance on defaults/inferences. It is not the probability that the recommendation is correct.

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Run Tests

```bash
python -m pytest
```

## Validation Assets

- `validation/FORMULA_REGISTER.md`
- `validation/ASSUMPTION_REGISTER.md`
- `validation/DECISION_RULE_REGISTER.md`
- `validation/INPUT_OUTPUT_TRACEABILITY.md`
- `validation/KNOWN_MODEL_LIMITATIONS.md`
- `validation/EXPECTED_RESULT_MATRIX.md`
- `validation/VALIDATION_DEFECT_REGISTER.md`
- `validation/RELEASE_READINESS_SCORECARD.md`
- `validation/MODEL_RISK_STATEMENT.md`
- `validation_data/`
- `external_reviews/`
- `docs/BUILD_0.9.6_VALIDATION_REPORT.md`
- `docs/BUILD_0.9.6.1_HOTFIX.md`
- `docs/SUPPLIER_INTELLIGENCE_UX_STANDARD.md`
- `docs/UI_OUTPUT_AUDIT.md`

## Current Release Position

Build 0.9.6.1 implementation is complete, but Portfolio Edition v1.0 is not yet approved. Remaining gates are:

1. Green GitHub Actions for Build 0.9.6.1
2. Streamlit smoke test
3. Live Packaging and Raw Material Supplier Intelligence validation
4. Closure of VAL-006 to VAL-009 after retest
5. Gemini independent validation report
6. Perplexity methodology review
7. Human procurement review or formal written waiver
8. Final release-readiness score of at least 9.0/10

## Model Risk Statement

AI Procurement Copilot is a decision-support and portfolio demonstration system. It does not autonomously approve suppliers, execute awards, replace due diligence, or substitute for commercial, legal, quality, financial, compliance, sustainability, or executive review.

## Operating Standard

GitHub is the canonical source of truth. Every milestone updates project status, changelog, build history, version manifest, QA evidence, defect governance and recovery documentation.
