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

### 1. Presentation Layer

Streamlit pages, controls, charts, tables, status messages, and downloads. Presentation code may format outputs but must not silently redefine business rules.

### 2. Input and Validation Layer

Handles demo data, CSV/Excel uploads, header recognition, required fields, supported categories, units, currencies, missing values, and validation warnings.

### 3. Normalization Layer

Preserves original quotation fields while producing explicit normalized currency, price, unit, FX rate, and comparison basis.

### 4. Procurement Intelligence Layer

Contains should-cost, landed-cost/TCO, risk, scoring, supplier comparison, Supplier 360, SRM, scenario, allocation, and negotiation calculations.

### 5. Governance Layer

Controls evidence quality, data confidence, recommendation eligibility, conflicting roles, validation warnings, human-review requirements, and final-award language.

### 6. Communication and Export Layer

Builds supplier clarification emails, executive memos, narratives, CSV/Excel/TXT outputs, and separate machine-readable audit downloads.

### 7. Quality Layer

Pytest regression coverage, Streamlit smoke tests, validation records, release scorecards, and manual acceptance evidence.

## Deployment Boundary

The application is a decision-support portfolio system. External ERP, supplier-master, live market-data, treasury, contract, and workflow integrations are outside v1.0.0 unless explicitly documented in a future release.

## Change Impact Map

| Change type | Minimum review |
|---|---|
| Labels, layout, explanatory copy | UI review + smoke test |
| Input column or schema | Data dictionary + validation + regression tests |
| Formula, weight, threshold, eligibility | Business-rules update + targeted and end-to-end tests |
| Export field or heading | Export regression + direct artifact review |
| Dependency version | Full tests + Streamlit smoke test |
| New LLM/API integration | Security, fallback, cost, privacy, and provider-independence review |
