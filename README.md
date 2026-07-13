# AI Procurement Copilot

**Release:** Portfolio Edition v1.0.0  
**Status:** Stable  
**Repository Owner:** pratikoperations

## Objective

AI Procurement Copilot is an interview-ready procurement decision-support platform covering category-specific should-cost, TCO, risk, Procurement Intelligence, Supplier 360, SRM, data-confidence governance, recommendation eligibility, category-aware communication, scenario testing, and executive reporting.

## Portability and Source of Truth

GitHub is the canonical source of truth. The application can run and be maintained without access to prior ChatGPT conversations. ChatGPT, Claude, Gemini, coding agents, and human developers must begin with:

1. `AI_HANDOFF_GUIDE.md`
2. `PORTABILITY_RISK_ASSESSMENT.md`
3. `PROJECT_ARCHITECTURE.md`
4. `BUSINESS_RULES.md`
5. `DATA_DICTIONARY.md`
6. `SETUP_GUIDE.md`
7. `CONTRIBUTING.md`

The stable v1.0.0 application runtime does not require ChatGPT. Future external AI-provider integrations must use environment-based credentials and separate validation.

## Release Position

Portfolio Edition v1.0.0 is the first stable release.

The release was approved after:

- Green GitHub Actions
- Regression and Streamlit smoke testing
- Packaging and Raw Material live validation
- Supplier Intelligence and Supplier 360 review
- Scenario-engine retesting
- Direct inspection of readable CSV, TXT, and Excel exports
- Validation of machine-readable audit separation
- Closure of all known Major and Critical release defects

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
- Supplier 360, performance, financial, ESG, innovation, and SRM views
- Evidence-governed Financial, ESG, Innovation, and long-term recommendation roles
- Category-aware supplier emails and executive memos
- Recommendation eligibility and business-rule validation
- Safe withholding of final-award language
- Scenario stress testing and allocation recommendations
- Business-readable CSV/Excel/TXT reports
- Separate machine-readable audit downloads
- Adversarial, external-file, UI, governance, currency, communication, export, and consistency tests

## Stable Release Integrity Controls

- PET Resin uses kg throughout the standard demo.
- No non-USD value is stored in a USD-labelled comparison field.
- Original Currency and Original Unit Price are preserved.
- Normalized Currency, Normalized Unit Price, FX Rate Used, Unit of Measure, and Comparison Basis are explicit.
- Unsupported currency conversion is blocked.
- Supplier communication changes by category and validation status.
- Insufficient-evidence suppliers cannot receive unsupported Most Innovative, Most Sustainable, Best Strategic Partner, or Best Long-Term Supplier roles.
- Exit Candidate and Development Candidate cannot be assigned to the same supplier.
- Visible risk terminology is Risk Resilience Score.
- Readable exports clearly distinguish RFQ scores from governed Supplier 360 scores.
- Freight stress changes unit and annual TCO for Packaging and Raw Material scenarios.
- Scenario rendering supports governed and legacy schema labels.

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Detailed setup instructions are in `SETUP_GUIDE.md`.

## Run Tests

```bash
python -m pytest
```

## Key Release Assets

- `RELEASE_NOTES.md`
- `PROJECT_STATUS.md`
- `VERSION_MANIFEST.md`
- `BUILD_HISTORY.md`
- `docs/RC_BUILD_ARCHIVE.md`
- `validation/FINAL_MANUAL_VALIDATION_RC1.2.3.md`
- `validation/VALIDATION_DEFECT_REGISTER.md`
- `validation/RELEASE_READINESS_SCORECARD.md`
- `docs/FUTURE_TIME_AWARE_ANALYTICS.md`

## Model Risk Statement

AI Procurement Copilot is a decision-support and portfolio demonstration system. It does not autonomously approve suppliers, execute awards, replace due diligence, or substitute for commercial, legal, quality, financial, compliance, sustainability, treasury, tax, or executive review.

## Next Planned Release

Version 1.1 is reserved for Time-Aware Procurement Analytics and remains a separate backlog and development stream. No Version 1.1 implementation is included in v1.0.0.

## Operating Standard

GitHub is the canonical source of truth. Stable-release maintenance must be limited to documented fixes. New features belong in a separate Version 1.1 development branch.
