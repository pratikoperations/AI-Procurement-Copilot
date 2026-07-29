# SAP Report-Family Mapping Guide

## Positioning

This guide supports approved file exports from SAP report families. It does not represent live SAP connectivity, a universal SAP schema, SAP certification, or write-back.

## Current sourcing-event sources

Preferred report family: `ME49`

Alternative report family: `ME80AN`

Approved Fiori or organization-specific exports may be supported when explicitly mapped to the canonical contract.

Suggested saved variant: `Z_COPILOT_RFQ_EVENT`

Expected selection controls may include:

- purchasing organization;
- collective number or RFQ range;
- supplier;
- material or material group;
- quotation status;
- event date range.

Expected fields should be mapped to canonical names through the alias registry and reviewed against the target SAP layout.

## Historical source

Preferred report family: `ME80FN`

Suggested saved variant: `Z_COPILOT_PO_HISTORY_24M`

Expected selection controls may include:

- purchasing organization;
- rolling 24-month document period;
- material group;
- plant;
- purchasing group;
- document category;
- completed items;
- retained deletion indicator.

## Variability statement

Exact fields and headers vary by SAP release, configuration, authorization, saved layout, custom fields, localization, and purchasing process. The adapter must therefore use:

- canonical fields;
- versioned aliases;
- explicit mapping review;
- source provenance;
- schema versioning.

## Export preparation

- Export `.xlsx`.
- Use one header row.
- Do not use merged cells.
- Remove totals and subtotals.
- Preserve leading zeros.
- Keep numeric values numeric.
- Use valid date values.
- Do not add report-title rows above headers.
- Retain deletion and status fields.
- Use sanitized or synthetic data in public deployments.

## Mapping confidence

- Exact approved alias: may be proposed automatically.
- Normalized approved alias: may be proposed automatically and displayed.
- Fuzzy similarity: suggestion only.
- Ambiguous or duplicate target: unresolved.
- High-risk field: requires explicit confirmation unless exact approved alias.
