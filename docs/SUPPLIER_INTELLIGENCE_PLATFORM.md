# Supplier Intelligence Platform

## Build

Build 0.9.5

## Purpose

Supplier Intelligence converts scored RFQ rows into explainable Supplier 360 profiles for category management, sourcing, supplier development, SRM, executive review, and portfolio demonstrations.

## Architecture

```text
Scored Supplier Data
├── Supplier Performance Engine
├── Financial Health Indicator Engine
├── ESG Intelligence Engine
├── Innovation Intelligence Engine
├── SRM Classification Engine
└── Supplier 360 Engine
    ├── Supplier Comparison
    ├── Recommendation Rankings
    └── Executive Supplier Narrative
```

## Supplier 360

Each profile includes commercial, operational, relationship, qualification, capacity, performance, financial, ESG, innovation, and governance fields.

Missing values are not silently invented. Transparent defaults are used only to keep the demo operational, and every defaulted field is listed in `defaults_used`.

## Performance Intelligence

Performance scoring covers quality, delivery, service, commercial competitiveness, corrective actions, continuous improvement, capacity reliability, and innovation contribution.

## Financial Health

Financial outputs are indicators based on available fields such as utilization, dependency, payment stress, and data completeness. They are not audited financial facts and do not claim bankruptcy probability.

## ESG Intelligence

ESG maturity expands the existing ESG score into environmental, social, governance, maturity, documentation, and corrective-action outputs.

## Innovation Intelligence

Innovation evaluates design, packaging or material innovation, cost reduction, automation, digital maturity, data sharing, AI readiness, continuous improvement, sustainability, and prototype speed.

## SRM Classification

Supported classes:

- Strategic
- Preferred
- Approved
- Transactional
- Development
- Exit Candidate

Each class includes governance cadence, relationship intensity, executive sponsorship, review frequency, rationale, and recommended strategy.

## Recommendation Governance

Recommendations are deterministic, role-specific, transparent, rule-guided, auditable, and not black-box AI. Human commercial, legal, quality, risk, and executive approval remains mandatory.

## Category Compatibility

Supplier Intelligence works with both Packaging Procurement and Raw Material Procurement using the selected category's scored supplier data. It does not replace category-specific should-cost, TCO, or risk engines.

## Known Limitations

- Synthetic or defaulted fields are not external supplier facts.
- Financial health is an indicator, not audited analysis.
- Country and site risk require verified external data.
- Historical performance requires real ERP, QMS, SRM, or scorecard feeds.
- Final supplier status requires human governance.
