# AI Procurement Copilot

**Release:** Portfolio Edition v1.0.1  
**Status:** Release candidate — closure review pending  
**Repository Owner:** pratikoperations

## Objective
AI Procurement Copilot is an interview-ready procurement decision-support platform covering category-specific should-cost, TCO, risk, Procurement Intelligence, Supplier 360, SRM, data-confidence governance, recommendation eligibility, category-aware communication, scenario testing, and executive reporting.

## Portability and Source of Truth
GitHub is the canonical source of truth. The application can run and be maintained without access to prior ChatGPT conversations. Begin with:

1. `AI_HANDOFF_GUIDE.md`
2. `PORTABILITY_RISK_ASSESSMENT.md`
3. `PROJECT_ARCHITECTURE.md`
4. `BUSINESS_RULES.md`
5. `DATA_DICTIONARY.md`
6. `SETUP_GUIDE.md`
7. `CONTRIBUTING.md`

The stable v1.0.1 application runtime does not require ChatGPT. Future external AI-provider integrations must use environment-based credentials and separate validation.

## Release Position
Portfolio Edition v1.0.1 is the stable maintenance release built on the first stable v1.0.0 portfolio baseline.

The v1.0.1 maintenance scope includes:
- governed USD, INR and Both display handling;
- Supplier Intelligence risk-adjusted TCO source preservation;
- preservation of original and normalized quotation data, FX metadata, units and comparison basis;
- preservation of supplier rankings, formulas, thresholds, recommendation eligibility and human approval controls;
- validated supplier selector and Supplier 360 behaviour;
- displayed edition and build metadata fixed to v1.0.1 with regression coverage.

No Version 1.1 or ERP feature implementation is included.

## Validation Position
- Standalone pre-maintenance main: 114 passed, 0 failed, 0 skipped, 1 warning; Streamlit smoke PASS.
- Reconstructed v1.0.1 candidate: 162 passed, 0 failed, 0 skipped, 1 warning; Streamlit smoke PASS.
- Final PR #9 Quality Checks: PASS.
- Recovery R1 hosted candidate startup: PASS.
- Six supplier profiles and USD/INR/Both modes: owner-observed acceptance completed.
- Primary `main` deployment after PR #9: owner-observed acceptance completed.
- Display-version correction on current main: v1.0.1 metadata and dedicated regression test present.

## Build Philosophy
The platform is transparent, rule-guided, auditable, and human-controlled. It does not autonomously approve suppliers. Inputs, assumptions, defaults, original quotations, normalized values, formulas, data gaps, evidence quality, and validation conditions remain visible.

## Implemented Capabilities
- Packaging Procurement and Raw Material Procurement engines
- Synthetic demo data and CSV/Excel RFQ upload
- Intelligent header recognition and unit normalization
- Explicit original and normalized currency/price fields
- Auditable FX rate and comparison basis
- Governed USD, INR and Both business-facing display modes
- Category-specific should-cost, TCO, risk, and scoring
- Procurement Intelligence and Supplier Intelligence
- Supplier 360, performance, financial, ESG, innovation, and SRM views
- Evidence-governed recommendations
- Category-aware supplier emails and executive memos
- Recommendation eligibility and business-rule validation
- Safe withholding of final-award language
- Scenario stress testing and allocation recommendations
- Business-readable CSV/Excel/TXT reports
- Separate machine-readable audit downloads
- Adversarial, external-file, UI, governance, currency, communication, export, consistency, and release-version tests

## Stable Release Integrity Controls
- No non-USD value is stored in a USD-labelled comparison field.
- Original Currency and Original Unit Price are preserved.
- Normalized Currency, Normalized Unit Price, FX Rate Used, Unit of Measure, and Comparison Basis are explicit.
- Unsupported currency conversion is blocked.
- No double conversion is permitted.
- Supplier rankings and procurement formulas remain unchanged by display-mode selection.
- Human approval remains mandatory.
- Readable and machine-readable exports remain separated.

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
- `VERSION_MANIFEST.md`
- `BUILD_HISTORY.md`
- `PROJECT_STATUS.md`
- `PROJECT_RECOVERY_MANIFEST.md`
- `RECOVERY_R1_BASELINE_VERIFICATION.md`
- `RECOVERY_R1_MAIN_TEST_EVIDENCE.md`
- `RECOVERY_R1_MAINTENANCE_TEST_EVIDENCE.md`
- `RECOVERY_R1_CURRENCY_VALIDATION_MATRIX.md`
- `RECOVERY_R1_SUPPLIER_SELECTOR_VALIDATION.md`
- `RECOVERY_R1_DEPLOYMENT_EVIDENCE.md`
- `RECOVERY_R1_MAINTENANCE_RECONCILIATION_PLAN.md`

## Model Risk Statement
AI Procurement Copilot is a decision-support and portfolio demonstration system. It does not autonomously approve suppliers, execute awards, replace due diligence, or substitute for commercial, legal, quality, financial, compliance, sustainability, treasury, tax, or executive review.

## Next Planned Release
Version 1.1 remains a separate, partially implemented and separately governed development stream. It is not part of v1.0.1 release closure.

## Operating Standard
Stable-release maintenance is limited to documented fixes. New features belong in a separately authorized Version 1.1 development stream.
