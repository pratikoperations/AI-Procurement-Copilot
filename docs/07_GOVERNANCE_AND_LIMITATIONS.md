# AI Procurement Copilot — Governance and Limitations

## Governance position

AI Procurement Copilot is a human-controlled procurement decision-support application. It structures analysis, evidence and communication but does not replace professional judgement, delegated authority or enterprise controls.

## Decision controls

- Validation precedes recommendation language.
- Missing or inconsistent evidence can block or condition outputs.
- Original and normalized quotation fields remain distinguishable.
- Assumptions, currency, units and comparison basis are visible.
- Business-readable reports are separated from machine-readable audit outputs.
- Human procurement review remains mandatory.

## EAS-BIV governance boundaries

### Authoritative calculations

- Existing business services remain authoritative.
- Formula metadata is documentation only and is never executed.
- The Governed Calculation Explorer does not reproduce calculations.
- A displayed formula must not be interpreted as an executable rule.

### Evidence and provenance

- Assumptions are classified as supplied, defaulted, inferred or derived.
- Unavailable intermediates and unresolved evidence are disclosed and are not inferred or reconstructed.
- SourceMate Basic presents registered internal references and evidence locations.
- SourceMate Basic does not browse the web, ingest documents, run OCR, use RAG, create embeddings or claim external verification.
- Evidence registration does not prove that evidence is present in every runtime export package.

### Trace and reconciliation coverage

The dedicated adapter-backed coverage remains:

- `REC-PET`
- `REC-KRF`
- `REC-COR`
- `REC-LAM`
- `REC-STL`
- `REC-SCORE-GEN`
- `REC-ELG`

All remaining non-export routes remain `unsupported_deferred_coverage`.

A deferred route may use its existing authoritative service but is not represented as adapter-reconciled. The application must not fabricate trace, intermediate or reconciliation evidence for it.

### Human decision boundary

- No autonomous supplier award is performed.
- No production allocation is executed.
- No approval persistence or workflow write-back exists.
- No ERP transaction is executed.
- Human procurement approval remains mandatory.

## Safe claims

The project can be described as:

- a governed procurement decision-support portfolio;
- a working RFQ comparison and sourcing-evaluation application;
- category-aware and validation-gated;
- supported by automated tests and staged release governance;
- containing a read-only ERP workbook structural preview;
- exposing calculation metadata, assumption provenance and deterministic traces;
- reconciling supported adapter-backed routes;
- presenting registered internal evidence locations and limitations;
- disclosing deferred coverage rather than overstating assurance.

## Claims that are not supported

Do not claim:

- production readiness;
- live SAP or Oracle integration;
- universal ERP or category compatibility;
- automated master-data matching;
- enterprise-scale performance;
- external evidence verification;
- physical supplier, legal, quality or compliance validation;
- realized savings;
- autonomous sourcing, recommendation, approval or award execution;
- production allocation;
- approval persistence;
- ERP write-back;
- validation using live organizational data;
- formal mobile, browser or WCAG certification.

## Security and privacy limitations

The application includes application-level file and package checks but is not enterprise-security certified. Production use would require identity and access management, malware scanning, secure hosting, privacy assessment, logging, monitoring, retention policies, incident controls and operational ownership.

## Model and data limitations

Recommendations are valid only relative to configured rules, assumptions and available data. Supplier financial, ESG, performance and risk views may be incomplete or provisional when evidence is missing. The application does not replace supplier audits, legal review, quality qualification, finance validation or compliance review.

## Hosted and mobile evidence boundary

Automated regression tests, source-level responsive controls and Streamlit smoke do not constitute physical browser-device certification. Until actual observations are supplied, desktop hosted, narrow viewport, Android portrait and Android landscape checks remain `not performed`.

## Historical release governance

The frozen historical baselines remain unchanged:

- v1.1: `b85cd37aaae709058eb15350d680b18c03da46ba`
- v1.2: `4803b1d72fa8a6509d9d7faf0e9decc677c447be`

Later governed work is additive. It does not rewrite historical release completion or convert the portfolio into a production, autonomous or live-ERP system.

## Current EAS-BIV baseline

- Gate 4 merge commit: `834b34db145cc0156196579f7419e7db7b438106`
- Accepted CI: Quality Checks run `816`
- Tests: `1011 passed`, `0 failures`, `0 errors`
- Human approval: mandatory
- Production status: not claimed
- External verification: not claimed

See:

- [EAS-BIV Final Closure](EAS_BIV_FINAL_CLOSURE.md)
- [EAS-BIV Interview Evidence Pack](EAS_BIV_INTERVIEW_EVIDENCE_PACK.md)
