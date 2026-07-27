# AI Procurement Copilot v1.2 — Governance and Limitations

## Governance position

AI Procurement Copilot is a human-controlled decision-support application. It structures procurement analysis and communication but does not replace professional judgement, delegated authority or enterprise controls.

## Decision controls

- Validation precedes recommendation language.
- Missing or inconsistent evidence can block or condition outputs.
- Original and normalized quotation fields remain distinguishable.
- Assumptions, currency, units and comparison basis are visible.
- Business-readable reports are separated from machine-readable audit outputs.
- Human procurement review remains mandatory.

## Safe claims

The project can be described as:

- a governed procurement decision-support portfolio;
- a working RFQ comparison and sourcing-evaluation application;
- category-aware and validation-gated;
- supported by automated tests and release governance;
- containing a read-only ERP workbook structural preview.

## Claims that are not supported

Do not claim:

- production readiness;
- live SAP or Oracle integration;
- universal ERP compatibility;
- automated master-data matching;
- enterprise-scale performance;
- realized savings;
- autonomous sourcing or award execution;
- ERP write-back;
- validation using live organizational data.

## Security and privacy limitations

The application includes application-level file and package checks but is not enterprise-security certified. Production use would require identity and access management, malware scanning, secure hosting, privacy assessment, logging, monitoring, retention policies and incident controls.

## Model and data limitations

Recommendations are valid only relative to configured rules, assumptions and available data. Supplier financial, ESG, performance and risk views may be incomplete or provisional when evidence is missing. The application does not replace supplier audits, legal review, quality qualification, finance validation or compliance review.

## Release governance

v1.1 remains complete and frozen at `b85cd37aaae709058eb15350d680b18c03da46ba`. v1.2 is a presentation-only release and may not expand procurement-engine or ERP-foundation scope. PR #14 remains draft and unmerged until audit, tests, hosted verification, mobile review and claim-safety review are complete.