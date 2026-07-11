# AI Procurement Copilot

**Edition:** Portfolio Edition v1.0  
**Current Build:** Build 0.9.6 — Independent Validation and Real-World Stress Testing  
**Status:** Validation Evidence Pending  
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
- Data-confidence scoring
- Recommendation eligibility gate
- Business-rule validation
- Safe withholding of final-award language
- Synthetic real-world and adversarial validation datasets
- Regression tests, CI, Streamlit smoke testing and governance documentation

## Build 0.9.6 Safety Controls

The application now checks:

- Required data and valid numeric ranges
- Positive price and annual volume
- Currency and UOM consistency
- Capacity sufficiency
- Allocation total and supplier-level feasibility
- Percentage conventions
- Missing, defaulted and inferred data
- Minimum supplier risk threshold
- Whether final award language is permitted

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
- `docs/EXTERNAL_FILE_VALIDATION_REPORT.md`

## Current Release Position

Build 0.9.6 implementation is complete, but Portfolio Edition v1.0 is not yet approved. Remaining gates are:

1. Green GitHub Actions for the complete Build 0.9.6 set
2. Live packaging and raw-material Streamlit validation
3. Gemini independent validation report
4. Perplexity methodology review
5. Human procurement review or formal written waiver
6. Closure of all Critical defects and mitigation of Major defects
7. Final release-readiness score of at least 9.0/10

## Model Risk Statement

AI Procurement Copilot is a decision-support and portfolio demonstration system. It does not autonomously approve suppliers, execute awards, replace due diligence, or substitute for commercial, legal, quality, financial, compliance, sustainability, or executive review.

## Operating Standard

GitHub is the canonical source of truth. Every milestone updates project status, changelog, build history, version manifest, QA evidence, defect governance and recovery documentation.
