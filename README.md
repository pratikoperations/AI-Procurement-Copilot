# AI Procurement Copilot

**Governed, category-aware procurement decision support for RFQ comparison and sourcing evaluation.**

> Portfolio demonstration · Read-only · Validation-gated · Human approval mandatory · No live ERP write-back

![AI Procurement Copilot v1.2 hero](docs/assets/hero/ai_procurement_copilot_v1_2_hero.svg)

**Hosted application:** `https://ai-procurement-copilot.streamlit.app/`

**Repository:** `pratikoperations/AI-Procurement-Copilot`

## Current repository status

- Public application identity: **AI Procurement Copilot v1.2 — Portfolio Presentation Release**
- Current controlled repository baseline before S1.5 completion: **`ab3648d62c4c61755b006fe5f85aa838988f3d2d`**
- Frozen v1.2 release baseline: **`4803b1d72fa8a6509d9d7faf0e9decc677c447be`**
- Frozen v1.1 baseline: **`b85cd37aaae709058eb15350d680b18c03da46ba`**
- Build Group S1: **S1.1–S1.4 complete; S1.5 accessibility and release assurance in controlled development**
- Controlled v1.3 workbook review and analytical-handoff foundation: **merged, governed and default-off unless explicitly enabled**
- Latest verified pre-S1.5 CI: **Quality Checks #617 — 437 passed, 0 failed; Streamlit smoke passed**
- Tag: **not created by deliberate release decision**
- GitHub Release: **not created by deliberate release decision**

The frozen v1.2 release record remains historical and unchanged. Later controlled builds add governed workbook intake, review orchestration, a default-off analytical handoff, UI hardening, responsive behavior and runtime efficiency without reclassifying the v1.2 release as incomplete.

## Business problem

Procurement teams often compare supplier quotations across disconnected spreadsheets, inconsistent assumptions and incomplete evidence. A lowest-price result can be mistaken for a best-value decision, while risk, delivery, quality, commercial terms and data confidence remain difficult to explain.

AI Procurement Copilot turns that fragmented review into a visible, governed decision-support workflow. It helps procurement professionals compare quotations, test sourcing scenarios, prepare negotiation positions and generate consistent review outputs without replacing human approval.

## Five business questions answered

1. Are supplier quotations sufficiently complete and valid for comparison?
2. How do quotations compare after governed currency, unit and comparison-basis handling?
3. Which commercial, cost, risk and sourcing factors materially affect the recommendation?
4. When should the system withhold award-oriented language because evidence is insufficient?
5. Which executive and downloadable outputs can support human procurement review?

## Workflow

1. Select a category, commodity and commercial assumptions.
2. Load synthetic data, a legacy RFQ CSV/XLSX, or the controlled governed-workbook review route when enabled.
3. Validate structure, completeness, currency, units and business rules.
4. Compare supplier cost, risk, performance, ESG and commercial conditions.
5. Review scenarios, allocation options and negotiation intelligence.
6. Generate executive-facing and machine-readable outputs.
7. Complete human procurement review and approval outside the application.

See [User Workflow](docs/03_USER_WORKFLOW.md).

## Key capabilities

- Packaging and raw-material procurement workflows
- Supplier quotation validation and governed comparison
- Original and normalized quotation-data preservation
- USD, INR and dual-display handling
- Category-specific should-cost, TCO, risk and scoring
- Procurement Intelligence and Supplier Intelligence views
- Supplier 360, performance, financial, ESG, innovation and SRM analysis
- Scenario testing, allocation and negotiation support
- Validation-gated recommendation language
- Executive memos, supplier communication and governed downloads
- Read-only ERP workbook structural preview with draft mappings
- Controlled governed-workbook review and default-off analytical handoff
- Responsive presentation and deterministic export caching

## What this project proves

- Practical understanding of procurement and sourcing workflows
- Ability to translate procurement requirements into a working application
- Category-aware comparison and decision-support logic
- Controlled validation and human-review gates
- Automated testing, branch discipline and staged release governance
- Clear separation between business-facing reports and audit outputs
- Governed ERP-export intake without overstating integration maturity
- Accessibility and responsive-presentation hardening appropriate to a portfolio application

## What it does not prove

- Production deployment readiness
- Live SAP or Oracle integration
- Universal ERP mappings
- Enterprise-scale performance
- Realized savings from live organizational use
- Autonomous sourcing, supplier approval or award execution
- ERP write-back
- Formal WCAG certification

## Architecture

![Five-stage architecture](docs/assets/diagrams/architecture_flow.svg)

The application keeps structural intake, governed review, analytical execution and human approval boundaries explicit. The controlled analytical-handoff route remains governed and default-off unless separately enabled.

See [Architecture](docs/04_ARCHITECTURE.md) and [Data and Validation](docs/05_DATA_AND_VALIDATION.md).

## Test and quality evidence

The repository uses automated checks for compilation, procurement calculations, validation, currency and unit integrity, exports, UI contracts, governed-workbook controls and Streamlit startup.

Current pre-S1.5 evidence:

- authoritative main SHA: `ab3648d62c4c61755b006fe5f85aa838988f3d2d`;
- Quality Checks run #617, run ID `30562810767`: **success**;
- 437 regression tests passed with 0 failures and 0 errors;
- canonical Streamlit smoke test passed;
- hosted startup and representative CSV, JSON and executive-output generation verified.

Final S1.5 evidence will be recorded after its draft PR, CI, hosted review and separately authorized merge.

See [Test Evidence](docs/06_TEST_EVIDENCE.md), [Release Record](docs/09_RELEASE_RECORD.md) and [S1 Build Closure](docs/S1_BUILD_CLOSURE.md).

## Governance and limitations

- Human procurement approval remains mandatory.
- Failed validation can block or condition recommendation language.
- The application does not execute transactions or mutate ERP systems.
- Illustrative monetary outputs are not realized-savings claims.
- Synthetic or sanitized data should be used for public demonstration.
- Production use would require identity, access, security, privacy, logging and operational controls outside this portfolio scope.
- Accessibility hardening is not a formal WCAG certification.

See [Governance and Limitations](docs/07_GOVERNANCE_AND_LIMITATIONS.md).

## Documentation by audience

- [Executive Overview](docs/01_EXECUTIVE_OVERVIEW.md)
- [Business Case Study](docs/02_BUSINESS_CASE_STUDY.md)
- [User Workflow](docs/03_USER_WORKFLOW.md)
- [Architecture](docs/04_ARCHITECTURE.md)
- [Data and Validation](docs/05_DATA_AND_VALIDATION.md)
- [Test Evidence](docs/06_TEST_EVIDENCE.md)
- [Governance and Limitations](docs/07_GOVERNANCE_AND_LIMITATIONS.md)
- [Demo Guide](docs/08_DEMO_GUIDE.md)
- [Release Record](docs/09_RELEASE_RECORD.md)
- [S1 Build Closure](docs/S1_BUILD_CLOSURE.md)

## Technical setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

Run tests:

```bash
python -m pytest
```

Detailed setup and portability guidance remain in `SETUP_GUIDE.md`, `AI_HANDOFF_GUIDE.md` and `PROJECT_ARCHITECTURE.md`.

## Version and build history

| Version/build | Position |
|---|---|
| v1.0.0 | First stable Portfolio Edition baseline |
| v1.0.1 | Governed maintenance release |
| v1.1 | Completed ERP structural foundation and read-only ERP Upload Preview; frozen at `b85cd37aaae709058eb15350d680b18c03da46ba` |
| v1.2 | Completed Portfolio Presentation Release; frozen at `4803b1d72fa8a6509d9d7faf0e9decc677c447be` |
| v1.3 foundation | Versioned workbook contracts, adapter, orchestration, governed review and default-off analytical handoff |
| S1.1–S1.4 | UI consistency, validation guidance, mobile responsiveness and runtime efficiency |
| S1.5 | Accessibility, final UX assurance and release reconciliation — controlled development |

## Historical relationship

The v1.2 release remains a completed frozen historical baseline. Subsequent authorized work is additive and controlled. It does not rewrite v1.2 history or convert the portfolio application into a production, autonomous or live-ERP system.
