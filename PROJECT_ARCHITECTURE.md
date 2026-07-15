# Project Architecture

## System Context

```text
User / Interviewer
      |
      v
Streamlit UI (`app.py`)
      |
      +--> Upload and demo-data ingestion
      +--> Validation and normalization
      +--> Procurement calculation modules
      +--> Decision, allocation, scenario and negotiation modules
      +--> Supplier Intelligence / Supplier 360
      +--> Communication and export builders
      |
      v
Business-readable screens and reports + machine-readable audit outputs
      |
      v
Human procurement review and approval
```

## Architectural Principles
- GitHub is the canonical source of truth.
- Business decisions remain explainable and auditable.
- Original inputs and normalized values remain distinguishable.
- Calculation logic is modular and testable.
- User-facing reports use procurement language.
- Technical audit outputs remain separate from executive outputs.
- Human approval remains outside the automated recommendation layer.
- External AI providers are optional assistive boundaries, never authoritative award engines.

## Application Layers
1. **Presentation layer:** Streamlit pages, controls, charts, tables, messages and downloads. Presentation must not silently redefine business rules.
2. **Input layer:** Demo data, RFQ files and future governed ERP workbooks.
3. **Validation layer:** Required fields, headers, workbook structure, units, currencies, missing values, severity and blocking controls.
4. **Normalization layer:** Original quotation preservation plus explicit normalized currency, price, unit, FX rate and comparison basis.
5. **Procurement decision engines:** Should-cost, TCO, risk, scoring, comparison, Supplier 360, SRM, scenarios, allocation and negotiation.
6. **Business-rule and recommendation governance:** Eligibility, evidence quality, confidence, conflicting roles, warnings, human review and award-language controls.
7. **UI and reporting layer:** Procurement Intelligence, Supplier Intelligence, executive narratives, readable reports and machine-readable evidence packages.
8. **Audit and evidence controls:** Traceable source fields, normalized fields, assumptions, warnings, validation results, recommendation rationale and export separation.
9. **Quality layer:** Pytest regression coverage, Streamlit smoke tests, validation records and manual acceptance evidence.

## Module Structure
| Responsibility | Authoritative module / path |
|---|---|
| Application orchestration | `app.py` |
| Sidebar assumptions | `modules/sidebar.py` |
| Demo and RFQ loading | `modules/data_loader.py` |
| Intelligent RFQ normalization | `modules/intelligent_rfq.py` |
| RFQ validation | `modules/validation.py` |
| Currency and unit governance | `modules/currency_unit_governance.py` |
| Packaging and raw-material cost/risk/TCO | `modules/category_*`, `modules/tco.py`, `modules/raw_material_*` |
| Supplier scoring and recommendation | `modules/scoring.py`, `modules/recommendation.py` |
| Allocation and scenarios | `modules/allocation*.py`, `modules/scenario*.py` |
| Negotiation and strategy | `modules/negotiation*.py`, `modules/strategy_engine.py` |
| Supplier Intelligence / Supplier 360 | `modules/supplier_comparison.py`, `modules/supplier_intelligence_ui.py` |
| Validation assurance and eligibility | `modules/validation_assurance.py` |
| Executive outputs and exports | `modules/executive_outputs.py`, `modules/exports.py` |
| Dashboard rendering | `modules/dashboard.py`, UI modules |
| Test architecture | `tests/`, `scripts/streamlit_smoke_test.sh`, `.github/workflows/quality-checks.yml` |

## Data Flow

```text
Source file or demo data
  -> intake controls
  -> structural and field validation
  -> normalization with source preservation
  -> category routing
  -> cost, TCO, risk and score engines
  -> eligibility and recommendation governance
  -> scenario / negotiation / Supplier 360 views
  -> readable executive outputs + machine-readable audit outputs
  -> human review and approval
```

## Upload and Normalization Pipeline
### Stable v1.0.0
- Supports governed demo and RFQ-oriented CSV/Excel intake through existing loader, validation and normalization modules.
- External ERP integration is outside stable scope.

### Verified Partial v1.1 Branch
The `v1.1-development` branch contains:
- `modules/erp_schema_registry.py`
- `modules/erp_mapping_profiles.py`
- `modules/erp_workbook_loader.py`
- `modules/erp_structure_validator.py`
- mapping profiles, sample workbooks, specifications and focused tests

Verified architecture boundary:

```text
ERP workbook
  -> safe workbook loader
  -> structural validator
  -> schema registry + mapping profile
  -> validation result
  -X-> procurement analysis until explicit approval
```

A complete orchestration pipeline, validation-report generator and Streamlit upload UI were not found in the verified branch comparison and must not be described as complete.

## Procurement Decision Engines
- Category-aware should-cost and TCO
- Packaging and raw-material risk models
- Supplier performance, ESG, financial and innovation indicators
- Weighted supplier scoring
- Recommendation eligibility and confidence
- Allocation and scenario analysis
- Negotiation intelligence and strategy
- Supplier 360 and SRM views

Exact formulas and thresholds remain governed by `FORMULA_TRACEABILITY_REGISTER.md`, `BUSINESS_RULES.md` and tests.

## Recommendation Governance
- Recommendations are decision support, not awards.
- Evidence limitations must reduce confidence or withhold conclusions.
- Conflicting supplier roles and missing due diligence must remain visible.
- Original data, normalized data and assumptions must remain auditable.
- Human procurement approval is mandatory before any award action.

## UI and Reporting Layer
- Streamlit is the current application interface.
- Business-facing screens must prioritize procurement-readable labels and selected display currency.
- Machine-readable evidence remains separate from executive-readable outputs.
- Supplier Intelligence includes a supplier selector in stable code.
- Currency-display maintenance exists on `maintenance/v1.0.1` and requires complete validation before promotion.

## Audit and Evidence Controls
Every decision package should preserve:
- source and normalized values
- units and currencies
- FX rate and comparison basis
- validation warnings and blocking conditions
- score and recommendation rationale
- human-review requirements
- readable and machine-readable output separation

## Test Architecture
Minimum gates:
1. Python compile/import validation
2. Focused module tests
3. Full `python -m pytest`
4. Streamlit startup smoke test
5. Currency and supplier-selector functional checks
6. Adversarial file tests
7. Direct export inspection
8. Manual procurement acceptance

Historical v1.0.0 evidence documents these gates as passed. Current maintenance and v1.1 branches require fresh evidence.

## Deployment Architecture
- Runtime: Streamlit application driven by `app.py`
- Dependencies: pinned in `requirements.txt`
- CI: `.github/workflows/quality-checks.yml`
- Smoke test: `scripts/streamlit_smoke_test.sh`
- Secrets: environment variables or Streamlit secrets; placeholders only in `.env.example`
- Current hosted deployment health was not independently verified in recovery.

## External AI-Provider Boundary
External LLM/API integration is not required for deterministic procurement calculations. Any future provider must pass security, privacy, cost, fallback, auditability and provider-independence review. Provider output may assist drafting or explanation but cannot silently modify calculations, eligibility or award decisions.

## Human Approval Boundary
The application ends at evidence-backed recommendation and communication support. Supplier qualification, due diligence, negotiation authority, sourcing approval, contracting and award remain human-controlled processes.

## Branch and Release Architecture
- `main`: stable v1.0.0 and canonical documentation
- `maintenance/v1.0.1`: documented defect fixes only
- `v1.1-development`: feature branch with partial ERP foundation
- `docs/project-recovery-2026-07-15`: recovery-control documentation only

Feature development must not resume until maintenance and development baselines are reconciled and approved.