# Build Group B2 — Canonical Ranking Input Contract

## Status
Additive contract version 1.3.1. The frozen v1.3.0 workbook contract is unchanged. This specification does not enable analytical handoff.

## Sheet
`SUPPLIER_RANKING_INPUTS` contains one supplier ranking record for a governed scope and measurement period.

## Scope precedence
1. `PLANT_MATERIAL_GROUP`
2. `MATERIAL_GROUP`
3. `PURCHASING_ORG`
4. `SUPPLIER_GLOBAL`

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

## Identity and scope
Required: record ID, version, supplier ID/name, purchasing organisation, scope, measurement start/end dates, active flag, source/provenance and approval fields. `MATERIAL_GROUP` is required for material-group scope. `PLANT` and `MATERIAL_GROUP` are required for plant-material-group scope.

## Modes
Quick RFQ requires OTIF, quality PPM, audit score, recyclability and certification score. Full Sourcing Review requires all ten ranking fields. Structurally nullable fields preserve reviewability; missing mode-mandatory evidence remains analytically blocking.

## Value origins
`SOURCE_MAPPED`, `USER_CONFIRMED`, `DERIVED_FROM_HISTORY`, `REFERENCE_ENRICHED`. `DEFAULTED_BY_ENGINE` is prohibited.

## Evidence statuses
`VALID`, `MISSING`, `INVALID_TYPE`, `OUT_OF_RANGE`, `STALE`, `AMBIGUOUS_SCOPE`, `AMBIGUOUS_SCALE`, `CONTRADICTORY`, `UNVERIFIED`.

## Percentage scale
Canonical percentages use 0–100 percentage points. Values such as `0.95` are ambiguous and must not be silently multiplied by 100.

## Cross-field controls
Audit score requires audit date, standard and reference. Certification score requires type, issuer, reference and validity dates. Carbon, EPR and PCR values require their respective methods, jurisdictions or references. Contradictory records at the same key and period are Fatal. Exact duplicates are informational. Overlapping active periods are Blocking.

## Boundary
Build B2 defines contract files and tests only. Build C2 must later implement parsing and validation. Build E remains review-only until separately reauthorized.