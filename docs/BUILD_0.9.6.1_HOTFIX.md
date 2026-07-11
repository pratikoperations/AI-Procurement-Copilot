# Build 0.9.6.1 Hotfix

## Title

Executive-Readable Supplier Intelligence UX Hotfix

## Root causes

1. Supplier Intelligence displayed nested engine outputs through a developer-oriented structured-data renderer.
2. Financial, ESG and innovation scores could appear stronger than the available evidence justified.
3. Machine-readable audit payloads were labelled with technical file-format terminology in the interface.

## Business impact

- Procurement users could mistake debug-style output for a finished executive product.
- A strong numerical score could be misread as verified evidence.
- Mobile usability and interview credibility were reduced.

## Resolution

- Replaced visible raw structured output with metric cards, score matrices, charts, evidence lists, action plans, warnings and governance panels.
- Added reusable executive UI components.
- Added evidence-completeness governance to financial, ESG and innovation engines.
- Capped displayed scores when evidence is insufficient or limited.
- Preserved raw calculations internally for auditability.
- Kept machine-readable data available only through downloads.
- Added readable Supplier 360 report download.

## Governance rules

- Financial completeness below 40%: Insufficient Data, displayed score capped at 50, due diligence mandatory.
- ESG completeness below 40%: Insufficient Data, score capped at 50, maturity cannot exceed Basic.
- Innovation completeness below 40%: Insufficient Data, score capped at 50, maturity cannot exceed Basic.
- Limited evidence between 40% and 69%: displayed score capped at 70 and human review required.

## Validation

Automated tests cover:

- No visible structured-data renderer in UI files
- No technical download labels
- Financial, ESG and innovation evidence caps
- Readable Supplier 360 report output
- Presence of executive UI components
- Preservation of raw internal scores for audit

## Status

Implementation completed. GitHub Actions, Streamlit smoke test and live Packaging/Raw Material validation remain pending.
