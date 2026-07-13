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
      +--> Decision, allocation, scenario, and negotiation modules
      +--> Supplier Intelligence / Supplier 360
      +--> Communication and export builders
      |
      v
Business-readable screens and reports + machine-readable audit outputs
```

## Architectural Principles

- GitHub is the canonical source of truth.
- Business decisions must remain explainable and auditable.
- Original inputs and normalized values must remain distinguishable.
- Calculation logic should be modular and testable.
- User-facing reports must use procurement language.
- Technical audit outputs must remain separate from executive outputs.
- Human approval remains outside the automated recommendation layer.

## Logical Layers

1. **Presentation:** Streamlit pages, controls, charts, tables, status messages and downloads. Presentation must not silently redefine business rules.
2. **Input and validation:** Demo data, CSV/Excel uploads, header recognition, required fields, units, currencies, missing values and warnings.
3. **Normalization:** Original quotation preservation plus explicit normalized currency, price, unit, FX rate and comparison basis.
4. **Procurement intelligence:** Should-cost, TCO, risk, scoring, comparison, Supplier 360, SRM, scenarios, allocation and negotiation.
5. **Governance:** Evidence quality, confidence, eligibility, conflicting roles, warnings, human review and award-language controls.
6. **Communication and exports:** Supplier emails, executive memos, narratives, CSV/Excel/TXT outputs and machine-readable audit packages.
7. **Quality:** Pytest regression coverage, Streamlit smoke tests, validation records and manual acceptance evidence.

## File and Module Ownership Map

| Workflow / responsibility | Authoritative file or module | Primary callable / contract |
|---|---|---|
| Application orchestration and UI flow | `app.py` | End-to-end composition of all engines and outputs |
| Sidebar assumptions | `modules/sidebar.py` | `render_sidebar` |
| Category profiles and routing | `modules/category_engine.py`, `modules/category_cost_router.py` | `ensure_category_profile`, `calculate_category_should_cost` |
| Demo and uploaded RFQ loading | `modules/data_loader.py` | `get_demo_data`, `load_uploaded_rfq` |
| Header aliases, fuzzy matching, unit normalization and upload diagnostics | `modules/intelligent_rfq.py` | `CANONICAL_COLUMNS`, `UNIT_ALIASES`, `normalize_rfq_dataframe` |
| RFQ and scored-output validation | `modules/validation.py` | `validate_rfq_dataframe`, `validate_scored_output` |
| Currency and comparison-basis governance | `modules/currency_unit_governance.py` | `normalize_comparison_basis`, `validate_category_unit` |
| Packaging risk | `modules/risk.py` | `calculate_risk`, payment and incoterm helpers |
| Raw-material risk | `modules/raw_material_risk.py` | `calculate_raw_material_risk` |
| Packaging TCO and freight shock | `modules/tco.py` | `calculate_supplier_tco`, freight-factor functions |
| Raw-material TCO | `modules/raw_material_tco.py` | `calculate_raw_material_tco` |
| Supplier performance | `modules/performance.py` | `calculate_performance_score` |
| ESG score | `modules/esg.py` | `calculate_esg_score` |
| Weighted supplier scoring | `modules/scoring.py` | `DEFAULT_WEIGHTS`, `RAW_MATERIAL_WEIGHTS`, `enrich_supplier_scores` |
| Best-value recommendation and confidence | `modules/recommendation.py` | `best_value_decision`, `recommendation_confidence`, `executive_value_breakdown` |
| Base allocation recommendation | `modules/allocation.py` | `recommend_allocation` |
| Optimized allocation | `modules/allocation_optimizer.py` | `optimize_allocation` |
| Scenario table | `modules/scenario.py` | `run_scenario_table` |
| Procurement-intelligence scenarios | `modules/scenario_engine.py` | `SCENARIOS`, `run_intelligence_scenario` |
| Negotiation simulation and playbook | `modules/negotiation.py` | `simulate_negotiation`, `generate_negotiation_playbook`, `govern_negotiation_brief` |
| Negotiation intelligence | `modules/negotiation_engine.py` | `build_negotiation_intelligence` |
| Procurement risk intelligence | `modules/risk_intelligence.py` | `assess_procurement_risks` |
| Strategy recommendation | `modules/strategy_engine.py` | `recommend_strategy` |
| Decision and executive narrative | `modules/decision_engine.py` | `generate_decision`, `generate_executive_narrative` |
| Supplier comparison / Supplier 360 data | `modules/supplier_comparison.py` | `build_supplier_intelligence` |
| Validation assurance, confidence, rules and eligibility | `modules/validation_assurance.py` | `run_validation_assurance`, `safe_executive_text` |
| Executive memo, supplier email, explainability and interview outputs | `modules/executive_outputs.py` | Output generator functions |
| Readable reports, Excel and machine-readable decision package | `modules/exports.py` | Readable builders, workbook and JSON builders |
| Dashboard rendering | `modules/dashboard.py` | `render_*` functions |
| Procurement and supplier intelligence rendering | `modules/procurement_intelligence_ui.py`, `modules/supplier_intelligence_ui.py` | UI render functions |
| Application metadata | `modules/config.py` | App name, build, edition and status constants |
| Regression tests | `tests/` | Pytest suite |
| Streamlit runtime smoke test | `scripts/streamlit_smoke_test.sh` | CI smoke check |
| CI version and validation pipeline | `.github/workflows/quality-checks.yml` | Python 3.11, compile, pytest and Streamlit smoke test |

Exact formulas and thresholds are indexed in `FORMULA_TRACEABILITY_REGISTER.md`; canonical input and output fields are indexed in `DATA_DICTIONARY.md`.

## Deployment Boundary

The application is a decision-support portfolio system. External ERP, supplier-master, live market-data, treasury, contract and workflow integrations are outside v1.0.0 unless explicitly documented in a future release.

## Change Impact Map

| Change type | Minimum review |
|---|---|
| Labels, layout, explanatory copy | UI review + smoke test |
| Input column or schema | Data dictionary + validation + regression tests |
| Formula, weight, threshold, eligibility | Formula register + business-rules update + targeted and end-to-end tests |
| Export field or heading | Export regression + direct artifact review |
| Dependency version | Full tests + Streamlit smoke test |
| New LLM/API integration | Security, fallback, cost, privacy and provider-independence review |