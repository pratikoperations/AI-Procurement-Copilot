# RC1 Download Content Audit

| File | Audience | Category-aware | Currency / unit integrity | Validation consistency | Readability | Status |
|---|---|---:|---:|---:|---:|---|
| Executive sourcing memo | Procurement leadership | Yes | Uses normalized comparison basis | Eligibility-aware | Executive text | Retest pending |
| Supplier clarification email | Supplier / buyer | Yes | Uses category unit and normalized price | Eligibility-aware | Business text | Retest pending |
| Supplier scores report | Procurement analyst | Yes | Original and normalized currency/price fields included | Eligibility and confidence included | Human-readable CSV | Retest pending |
| Supplier comparison report | Procurement leadership | Yes | Normalized price and UOM visible | Governed scores and status included | Human-readable CSV | Retest pending |
| Excel analysis | Procurement team | Yes | Readable sheets plus audit sheet | Governed context included | Business-readable workbook | Retest pending |
| Executive supplier narrative | Procurement leadership | Yes | Uses governed indicators | Final output withheld when blocked | Executive text | Retest pending |
| Supplier 360 readable report | SRM / category manager | Yes | Category and evidence context | Human approval stated | Readable TXT | Retest pending |
| Decision machine-readable audit data | Audit / developer | Internal | Raw and normalized fields allowed | Eligibility payload included | Machine-readable only | Retest pending |
| Supplier 360 machine-readable audit data | Audit / developer | Internal | Raw evidence allowed | Governance fields retained | Machine-readable only | Retest pending |

## Manual inspection requirement

Open every downloaded file after deployment and confirm:

- No business-readable file exposes snake_case fields.
- PET Resin uses kg.
- Currency and normalized price are consistent.
- Blocked outputs do not imply award.
- Recommendation roles match evidence status.
