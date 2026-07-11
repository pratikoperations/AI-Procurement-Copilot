# UI Output Audit

## Scope checked

- `app.py`
- `modules/supplier_intelligence_ui.py`
- `modules/procurement_intelligence_ui.py`
- `modules/dashboard.py`
- `modules/executive_outputs.py`
- `modules/supplier_comparison.py`

## Findings

The primary raw-output defect was in Supplier Intelligence, where nested performance, financial, ESG, innovation and SRM objects were displayed directly through Streamlit's structured-data renderer.

## Replacements

- Performance: metric cards, score matrix, bar chart, strengths, gaps and action plan
- Financial: assessment status, completeness, governed displayed score, risk indicators, evidence, due-diligence actions and disclaimer
- ESG: maturity cards, dimension chart, evidence gaps, document checklist and corrective actions
- Innovation: maturity cards, dimension chart, strengths, gaps, opportunity matrix and agenda
- SRM: classification, strategic index, governance matrix, rationale and relationship strategy
- Supplier 360: identity, commercial, capacity, continuity, relationship and data-quality matrices
- Recommendations: readable matrix
- Comparison: executive comparison matrix

## Machine-readable outputs retained

- Decision audit data download
- Supplier 360 audit data download

These files are download-only and are not rendered on-screen.

## Validation statement

No `st.json` renderer remains in the principal application UI files. Automated tests protect this requirement and prohibit technical download labels.

## Remaining manual check

After deployment, inspect every tab on mobile and desktop to confirm that no third-party component or newly generated narrative exposes raw technical payloads.
