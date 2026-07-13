# Data Dictionary

## Purpose

This is the cross-LLM and developer reference for core business concepts. Exact column names may vary by supported upload template; validation and normalization code remains authoritative.

| Concept | Meaning | Governance requirement |
|---|---|---|
| Supplier | Quoting or assessed supplier identifier | Must remain traceable across inputs and outputs |
| Category / Commodity | Procurement context such as Packaging or Raw Material | Controls terminology, should-cost logic, unit expectations, and communications |
| Original Currency | Currency supplied in the quotation | Preserve unchanged |
| Original Unit Price | Supplier-submitted unit price | Preserve unchanged |
| Normalized Currency | Currency used for comparison | Must be explicitly labelled |
| Normalized Unit Price | Converted comparison price | Must use supported FX and unit logic |
| FX Rate Used | Rate applied during normalization | Must be visible and auditable |
| Unit of Measure | Comparison unit, such as kg | Must be category-appropriate and consistent |
| Comparison Basis | Explanation of normalization basis | Must be explicit in readable outputs |
| Annual Volume | Demand basis for annualized calculations | Unit must align with unit price |
| Freight / Logistics | Transport-related cost input | Included consistently in TCO and scenario stress |
| Should Cost | Modelled cost benchmark | Assumptions and category basis must be disclosed |
| Annual TCO | Annualized total cost of ownership | Currency and volume basis must be explicit |
| Risk Resilience Score | User-visible risk capability indicator | Do not relabel as ambiguous raw risk score |
| RFQ Performance Score | Score derived from quotation/workflow inputs | Keep distinct from Supplier 360 assessment |
| Supplier 360 Score | Governed broader supplier assessment | Subject to evidence and confidence controls |
| Data Confidence | Reliability/completeness indicator | Lower when evidence is missing or weak |
| Eligibility Status | Whether a recommendation/action is supportable | Controls award language and human review |
| Validation Warning | Human-readable data or rule warning | Must not be suppressed from decision outputs |
| Human Review Required | Explicit review flag | Mandatory when governance conditions require it |

## Missing Values

- Mandatory commercial or normalization fields: block or mark ineligible.
- Optional evidence fields: retain with reduced confidence and capped conclusions.
- Unknown values must remain unknown; do not replace with fabricated defaults.
- Any approved default must be visible, documented, and tested.

## Sensitive Data

Use synthetic or de-identified data in the public portfolio repository. Do not commit supplier-confidential information, personal data, credentials, contracts, or proprietary pricing without authorization.
