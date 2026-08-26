# AI Procurement Copilot

**Governed, category-aware procurement decision support for RFQ comparison, sourcing evaluation and calculation explainability.**

> Portfolio demonstration · Read-only governance layers · Validation-gated · Human approval mandatory · No live ERP write-back

![AI Procurement Copilot v1.2 hero](docs/assets/hero/ai_procurement_copilot_v1_2_hero.svg)

**Hosted application:** `https://ai-procurement-copilot.streamlit.app/`

**Repository:** `pratikoperations/AI-Procurement-Copilot`

## Current repository status

- Current public portfolio baseline on `main`: **`dc05fcb86e5be53212443834b3d6c46cc5aeca5c`**.
- Operating mode: **portfolio/interview product under stabilization freeze**, with only bounded public-launch hardening permitted; routine cosmetic and feature expansion remains closed.
- SourceMate is a **project-wide, read-only, deterministic assistant with chat-style UX, browser-session conversation continuity and page-aware governed context**. It is available from the main procurement application, Governed Calculation Explorer and ERP Upload Preview. It does not browse the web, call an external LLM, use RAG, recalculate authoritative procurement results or execute procurement actions.
- Recent presentation hardening includes improved workflow hierarchy, result presentation, selectable-control distinction and public-upload confidentiality warnings. These changes do not alter procurement calculations, scoring, eligibility, allocation, recommendations or SourceMate decision logic.
- Governed Calculation Explorer contract: **`AIPC-GOVERNED-EXPLORER-1.0`**.
- SourceMate conversation contract: **`AIPC-SOURCEMATE-PROJECT-WIDGET-BIV-1.0`**.
- Calculation trace contract: **`AIPC-CALC-TRACE-1.0`**.
- Latest accepted exact-head validation before the current public baseline merge: source head **`b895815fe1c0511b7f025c53773ca2e5ba60dbdc`**; Quality Checks run **1117** / run ID **`32959567882`**, Python 3.11.16, **1534 passed, 0 failures**, compilation/Ruff/type checks/dependency audit/Streamlit smoke passed; Mobile Browser Acceptance run **136** / run ID **`32959567861`**, passed.
- Test warning boundary: **two non-failing warnings** in the latest regression run, including the pre-existing pandas FutureWarning; no test failure.
- Public upload safety is now explicit: users are instructed to use only synthetic or sanitized files and not to upload confidential supplier quotations, contracts, proprietary company information, personal data, credentials or commercially sensitive documents.
- Frozen v1.2 release baseline: **`4803b1d72fa8a6509d9d7faf0e9decc677c447be`**.
- Frozen v1.1 baseline: **`b85cd37aaae709058eb15350d680b18c03da46ba`**.
- Tag and GitHub Release for the later stabilized portfolio build: **not created by deliberate governance decision**.

The v1.1 and v1.2 release records remain historical and unchanged. Later governed work is additive and does not reclassify those releases as incomplete or convert this portfolio application into production enterprise software.

## Business problem

Procurement teams often compare supplier quotations across disconnected spreadsheets, inconsistent assumptions and incomplete evidence. A lowest-price result can be mistaken for a best-value decision, while the formula source, assumption provenance, trace identity and evidence quality remain difficult to explain.

AI Procurement Copilot turns that fragmented review into a visible, governed decision-support workflow. It helps procurement professionals compare quotations, test sourcing scenarios, prepare negotiation positions and inspect calculation evidence without replacing human approval.

## Five business questions answered

1. Are supplier quotations sufficiently complete and valid for comparison?
2. How do quotations compare after governed currency, unit and comparison-basis handling?
3. Which commercial, cost, risk and sourcing factors materially affect the recommendation?
4. Which calculations, assumptions, versions and evidence support a result?
5. When should the system withhold or qualify award-oriented language because evidence is incomplete?

## Workflow

1. Select a category, commodity and commercial assumptions.
2. Load synthetic data, a sanitized RFQ CSV/XLSX, or the controlled governed-workbook review route when enabled.
3. Validate structure, completeness, currency, units and business rules.
4. Compare supplier cost, risk, performance, ESG and commercial conditions.
5. Review scenarios, allocation options and negotiation intelligence.
6. Inspect the Governed Calculation Explorer, assumption provenance, trace, reconciliation and SourceMate evidence.
7. Generate executive-facing and machine-readable outputs.
8. Complete human procurement review and approval outside the application.

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
- Governed calculation catalogue and assumption provenance
- Deterministic calculation traces with retained configuration versions
- Reconciliation and export evidence assurance
- Governed Calculation Explorer with readable evidence and calculation payloads
- Project-wide SourceMate with chat-style UX, browser-session conversation continuity and page-aware governed context
- Explicit adapter-backed and `unsupported_deferred_coverage` states
- Evidence-derived, read-only human-review checklist
- Responsive/mobile acceptance coverage for governed test profiles
- Explicit public-demo upload/privacy warnings

## EAS-BIV coverage

Dedicated adapter-backed coverage remains exactly:

- `REC-PET`
- `REC-KRF`
- `REC-COR`
- `REC-LAM`
- `REC-STL`
- `REC-SCORE-GEN`
- `REC-ELG`

All remaining non-export routes remain `unsupported_deferred_coverage`. Deferred routes are not represented as adapter-reconciled and do not receive fabricated traces.

## What this project proves

- Practical understanding of procurement and sourcing workflows
- Ability to translate procurement requirements into a working application
- Category-aware comparison and decision-support logic
- Controlled validation and human-review gates
- Calculation metadata, assumption provenance and deterministic trace design
- Reconciliation and evidence-boundary governance
- Automated testing, branch discipline and exact-head change governance
- Clear separation between business-facing reports and audit outputs
- Governed ERP-export intake without overstating integration maturity
- A project-wide read-only assistant grounded in existing governed application evidence
- Scope discipline through explicit deferred coverage and stabilization freeze
- Public-demo privacy and data-handling boundary awareness

## What it does not prove

- Production deployment readiness
- Live SAP or Oracle integration
- Universal ERP or category compatibility
- Enterprise-scale performance or security
- External evidence verification
- Realized savings from live organizational use
- Autonomous sourcing, supplier approval or award execution
- Approval persistence, production allocation or ERP write-back
- Formal browser/mobile or WCAG certification

## Architecture

![Five-stage architecture](docs/assets/diagrams/architecture_flow.svg)

The application keeps structural intake, analytical execution, explainability, evidence presentation and human approval boundaries explicit. Existing business services remain authoritative; formula metadata is documentation only.

See [Architecture](docs/04_ARCHITECTURE.md), [Data and Validation](docs/05_DATA_AND_VALIDATION.md) and [EAS-BIV Final Closure](docs/EAS_BIV_FINAL_CLOSURE.md).

## Current test and quality evidence

Latest accepted exact-head evidence for the code tree that produced the current public baseline:

- Validated source head: `b895815fe1c0511b7f025c53773ca2e5ba60dbdc`;
- resulting `main` baseline: `dc05fcb86e5be53212443834b3d6c46cc5aeca5c`;
- Quality Checks run 1117, run ID `32959567882`;
- Python 3.11.16;
- 1534 regression tests passed with 0 failures;
- Python compilation passed;
- Ruff governed checks passed;
- targeted mypy checks passed;
- dependency audit reported no known vulnerabilities;
- canonical Streamlit smoke test passed;
- Mobile Browser Acceptance run 136, run ID `32959567861`, passed.

Automated browser acceptance is evidence for the governed test profiles, not certification across every physical device or browser. Hosted behavior is manually rechecked when a hosted defect correction or launch-readiness gate requires it.

Historical gate-specific evidence remains available in [Test Evidence](docs/06_TEST_EVIDENCE.md), [EAS-BIV Interview Evidence Pack](docs/EAS_BIV_INTERVIEW_EVIDENCE_PACK.md) and [Release Record](docs/09_RELEASE_RECORD.md).

## Governance and limitations

- Human procurement approval remains mandatory.
- Formula metadata is documentation only and is never executed.
- Existing business services produce authoritative results.
- Unavailable evidence is disclosed and is not reconstructed.
- SourceMate is read-only, uses current governed application/project evidence and does not perform external verification.
- SourceMate has no web browsing, external LLM, RAG, hidden recalculation, autonomous recommendation, supplier approval, award, production allocation or ERP write-back authority.
- Deferred routes are not represented as adapter-reconciled.
- The application does not execute transactions or mutate ERP systems.
- Illustrative monetary outputs are not realized-savings claims.
- Synthetic or sanitized data should be used for public demonstration.
- Public users should not upload confidential supplier quotations, contracts, proprietary company information, personal data, credentials or commercially sensitive documents.
- Production use would require enterprise identity, security, privacy, logging, monitoring and operational controls.

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
- [EAS-BIV Final Closure](docs/EAS_BIV_FINAL_CLOSURE.md)
- [EAS-BIV Interview Evidence Pack](docs/EAS_BIV_INTERVIEW_EVIDENCE_PACK.md)

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
| S1.5 | Accessibility and final UX assurance completed |
| S1.5.1 | Responsive containment correction completed through PR #29 |
| EAS-BIV Gate 1A | Calculation catalogue and assumption provenance |
| EAS-BIV Gate 2 | Governed parameter precedence and deterministic traces |
| EAS-BIV Gate 3 | Reconciliation and export evidence assurance |
| EAS-BIV Gate 4 | Governed Calculation Explorer and initial SourceMate Basic Evidence View |
| EAS-BIV Gate 5 | Documentation, evidence and final closure |
| Stabilized portfolio build — Aug 2026 | Cross-category consistency, Steel shared-workflow reconciliation, project-wide SourceMate, chat-style SourceMate UX, decision-result hierarchy, selectable-control visual distinction, mobile assurance, hosted defect corrections and public-demo upload/privacy hardening; no production-scope expansion |

## Historical relationship

- Historical EAS-BIV Gate 5 evidence anchor: starting baseline `834b34db145cc0156196579f7419e7db7b438106`; Quality Checks run 816; 1011 regression tests passed at that historical gate.
- The v1.1 and v1.2 releases remain completed frozen historical baselines. Subsequent authorized work is additive, governed and stabilization-frozen except for bounded launch-readiness corrections. It does not rewrite release history or convert the portfolio application into a production, autonomous or live-ERP system.
