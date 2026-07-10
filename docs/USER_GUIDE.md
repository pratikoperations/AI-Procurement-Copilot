# User Guide

## Purpose

AI Procurement Copilot converts supplier RFQ data into a transparent, decision-ready sourcing recommendation.

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Run Tests

```bash
pytest -q
```

## Input Methods

### Synthetic Demo

Select **Synthetic Demo** in the sidebar. The app loads a ready-to-use packaging RFQ with three suppliers.

### RFQ Upload

Select **Upload RFQ CSV/Excel** and upload a file matching the sample schema in:

`sample_data/sample_packaging_rfq.csv`

### Required Columns

- Supplier
- Quoted Unit Price USD
- MOQ
- Lead Time Days
- Payment Terms
- Incoterms

### Recommended Optional Columns

- OTIF %
- Quality PPM
- Audit Score
- Complaint Rate %
- Capacity Buffer %
- Recyclability
- Certification
- Carbon Score
- EPR Readiness
- PCR Content %
- Supplier Capacity

If optional columns are absent, the model uses defined defaults and displays a warning.

## Sidebar Assumptions

Users can adjust:

- USD/INR exchange rate
- Display currency
- Annual volume
- Raw material shock
- Freight shock
- Demand change
- Maximum supplier allocation
- Minimum backup allocation
- Minimum risk score
- Minimum ESG score

## Application Workflow

### Decision Summary

Shows the recommended supplier, lowest-price comparison, executive value metrics, and supplier scorecard.

### Cost & Risk Analysis

Shows packaging should-cost, TCO breakdown, and visible risk assumptions.

### Scenarios & Negotiation

Shows allocation recommendation, scenario stress test, negotiation simulation, and negotiation playbook.

### Executive Outputs

Generates:

- Executive sourcing memo
- Supplier clarification email
- AI-style explainability panel

### Interview Guide

Provides a structured explanation of the project and a recommended demo flow.

## Output Interpretation

The highest-ranked supplier is the **best-value recommendation**, not automatically the lowest quote. The recommendation considers:

- Risk-adjusted TCO
- Payment terms
- MOQ
- Lead time
- Supplier risk
- Supplier performance
- ESG
- Allocation constraints

## Governance

The app is a transparent, rule-guided decision-support tool. It does not make an autonomous black-box award decision. Procurement retains decision ownership.
