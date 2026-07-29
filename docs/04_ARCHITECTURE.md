# AI Procurement Copilot v1.2 — Architecture Summary

## Architectural intent

The application separates presentation, procurement calculations, validation, intelligence, exports and ERP preview responsibilities. Version 1.2 changes presentation and documentation only; it does not expand the frozen v1.1 product logic.

## Five-stage flow

```text
Procurement and RFQ Data
        ↓
Validation and Controlled Transformation
        ↓
Category-Aware Comparison and Decision Logic
        ↓
Business-Facing Views and Downloads
        ↓
Human Procurement Review and Action
```

## Application layers

### 1. Input and configuration

- Streamlit public application
- Category, commodity, volume, currency and scenario assumptions
- Synthetic data and supported RFQ upload

### 2. Validation and governance

- Structural and field validation
- Currency and unit governance
- Business-rule checks
- Data confidence and recommendation eligibility

### 3. Procurement decision support

- Should-cost and TCO
- Risk and scoring
- Supplier comparison
- Scenario and allocation logic
- Negotiation and strategy support
- Procurement and Supplier Intelligence

### 4. Presentation and outputs

- Executive-first landing view
- Compact section selector
- Business-readable reports
- Separate machine-readable audit outputs

### 5. Human review

The system provides analysis and controlled communication. Procurement approval, due diligence and execution remain outside the application.

## ERP Preview isolation

The ERP Upload Preview uses dedicated workbook-loader, schema, structure-validator, mapping-profile and presenter components. It is isolated from procurement engines and does not perform normalization, matching, integration or write-back.

## Technical boundaries

- Python and Streamlit portfolio architecture
- No application database or intentional workbook persistence
- No live SAP or Oracle API
- No autonomous agent or award execution
- Production security, identity, monitoring and scale controls are outside scope

## Canonical detailed sources

For deeper engineering evidence, see `PROJECT_ARCHITECTURE.md`, `ARCHITECTURE.md`, `BUSINESS_RULES.md`, `DATA_DICTIONARY.md` and the ERP planning records.