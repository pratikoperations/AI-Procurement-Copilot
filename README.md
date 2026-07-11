# AI Procurement Copilot

**Edition:** Portfolio Edition v1.0  
**Current Build:** Build 1.0 RC1.2 — Export Integrity and Category-Aware Communication Hotfix  
**Status:** Release Candidate Validation Pending  
**Repository Owner:** pratikoperations

## Objective

AI Procurement Copilot is an interview-ready procurement decision-support project covering category-specific should-cost, TCO, risk, Procurement Intelligence, Supplier 360, SRM, data-confidence governance, recommendation eligibility, category-aware communication, and executive reporting.

## Build Philosophy

The platform is transparent, rule-guided, auditable, and human-controlled. It does not autonomously approve suppliers. Inputs, assumptions, defaults, original quotations, normalized values, formulas, data gaps, evidence quality, and validation conditions remain visible.

## Implemented Capabilities

- Packaging Procurement and Raw Material Procurement engines
- Synthetic demo data and CSV/Excel RFQ upload
- Intelligent header recognition and unit normalization
- Explicit original and normalized currency/price fields
- Auditable FX rate and comparison basis
- Category-specific should-cost, TCO, risk, and scoring
- Procurement Intelligence and Supplier Intelligence
- Evidence-governed Financial, ESG, Innovation, and long-term recommendation roles
- Category-aware supplier emails and executive memos
- Recommendation eligibility and business-rule validation
- Safe withholding of final-award language
- Business-readable CSV/Excel/TXT reports
- Separate machine-readable audit downloads
- Adversarial, external-file, UI, governance, currency, communication, export, and consistency tests

## RC1.2 Integrity Controls

- PET Resin uses kg throughout the standard demo.
- No non-USD value is stored in a USD-labelled comparison field.
- Original Currency and Original Unit Price are preserved.
- Normalized Currency, Normalized Unit Price, FX Rate Used, Unit of Measure, and Comparison Basis are explicit.
- Unsupported currency conversion is blocked.
- Supplier communication changes by category and validation status.
- Insufficient-evidence suppliers cannot receive unsupported Most Innovative, Most Sustainable, Best Strategic Partner, or Best Long-Term Supplier roles.
- Exit Candidate and Development Candidate cannot be assigned to the same supplier.
- Visible risk terminology is Risk Resilience Score.

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Run Tests

```bash
python -m pytest
```

## Key Validation Assets

- `validation/VALIDATION_DEFECT_REGISTER.md`
- `validation/RELEASE_READINESS_SCORECARD.md`
- `validation/RC1_MANUAL_VALIDATION_CHECKLIST.md`
- `validation/RC1_MANUAL_DEFECT_LOG.md`
- `docs/BUILD_1.0_RC1.2_HOTFIX.md`
- `docs/RC1_DOWNLOAD_CONTENT_AUDIT.md`
- `docs/CURRENCY_AND_UNIT_GOVERNANCE.md`
- `docs/CATEGORY_AWARE_COMMUNICATION_STANDARD.md`

## Current Release Position

RC1.2 implementation is complete. Portfolio Edition v1.0 remains untagged until:

1. RC1.2 GitHub Actions are green.
2. Streamlit loads Packaging and Raw Material workflows.
3. Standard PET Resin demo no longer falsely blocks on currency.
4. Downloaded Excel, CSV, TXT, and audit files open and match on-screen status.
5. RC1-DEF-005 through RC1-DEF-011 are closed after retest.
6. Independent reviews are completed or formally waived.
7. Final release-readiness score remains at least 9.0/10.

## Model Risk Statement

AI Procurement Copilot is a decision-support and portfolio demonstration system. It does not autonomously approve suppliers, execute awards, replace due diligence, or substitute for commercial, legal, quality, financial, compliance, sustainability, treasury, tax, or executive review.

## Operating Standard

GitHub is the canonical source of truth. Feature development remains frozen until Portfolio Edition v1.0 release approval.
