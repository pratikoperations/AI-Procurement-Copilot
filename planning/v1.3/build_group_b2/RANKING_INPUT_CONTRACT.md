# Build Group B2 — Canonical Ranking Input Contract

## Status
Additive contract version 1.3.1. The frozen v1.3.0 workbook contract is unchanged. This specification does not enable analytical handoff.

## Sheet
`SUPPLIER_RANKING_INPUTS` contains one supplier ranking record for a governed scope and measurement period.

## Local schema resolution
The v1.3.1 schema references the frozen v1.3.0 RFQ, history and metadata row definitions through `urn:aipc:minimum-workbook:1.3.0`. Validators must register the frozen local schema file against that URN. Network resolution is prohibited.

## Scope precedence
1. `PLANT_MATERIAL_GROUP`
2. `MATERIAL_GROUP`
3. `PURCHASING_ORG`
4. `SUPPLIER_GLOBAL`

`SUPPLIER_GLOBAL` and `PURCHASING_ORG` prohibit material group and plant. `MATERIAL_GROUP` requires material group and prohibits plant. `PLANT_MATERIAL_GROUP` requires both.

## Canonical ranking fields
- `OTIF_PERCENT`: number, 0–100 percentage points.
- `QUALITY_PPM`: number, minimum 0.
- `SUPPLIER_AUDIT_SCORE`: number, 0–100.
- `COMPLAINT_RATE_PERCENT`: number, 0–100 percentage points.
- `CAPACITY_BUFFER_PERCENT`: number, 0–100 percentage points.
- `RECYCLABILITY_PERCENT`: number, 0–100 by weight.
- `CERTIFICATION_SCORE`: number, 0–100.
- `CARBON_SCORE`: number, 0–100.
- `EPR_READINESS_SCORE`: number, 0–100.
- `PCR_CONTENT_PERCENT`: number, 0–100 by weight.

## Modes
Quick RFQ requires OTIF, quality PPM, audit score, recyclability and certification score. Full Sourcing Review requires all ten. These mode requirements are normative Build C2 eligibility rules, not JSON Schema `required` fields.

## Source-versus-derived evidence
`SOURCE_EVIDENCE_STATUS` is optional and non-authoritative. `CANONICAL_EVIDENCE_STATUS` is computed by Build C2 for each canonical field and cannot be asserted by the workbook.

## Per-field value origins
`VALUE_ORIGINS` is keyed by canonical ranking field and supports mixed origins in one row: `SOURCE_MAPPED`, `USER_CONFIRMED`, `DERIVED_FROM_HISTORY`, and `REFERENCE_ENRICHED`. `DEFAULTED_BY_ENGINE` is prohibited.

## Derived adapter result contract
For each populated ranking field, Build C2 must eventually return: canonical field, canonical value, canonical evidence status, value origin, source reference, and validation findings. B2 defines this structure only; it does not implement it.

## Percentage scale
Canonical percentages use 0–100 percentage points. Values such as `0.95` are not silently multiplied by 100. Numeric bounds are JSON Schema enforced; semantic 0–1 versus 0–100 ambiguity is Build C2 enforced.

## Rule classification
- `JSON_SCHEMA_ENFORCED`: types, numeric ranges, scope presence/prohibition, supporting evidence presence, per-field origin presence, closed enums, additional-property rejection and SHA-256 format.
- `BUILD_C2_ENFORCED`: semantic scale ambiguity, mode eligibility, freshness, cross-row duplicate/contradiction/overlap, scope precedence and canonical evidence-status derivation.
- `DOCUMENTARY_POLICY`: metric meaning, approved evidence sources, migration and analytical blocking.

## Alias boundary
Every listed non-canonical alias requires confirmation. Any ranking or evidence field without a listed alias requires the exact canonical header.

## Boundary
Build B2 defines contract files and tests only. Build C2 must later implement parsing and validation. Build E remains review-only until separately reauthorized.
