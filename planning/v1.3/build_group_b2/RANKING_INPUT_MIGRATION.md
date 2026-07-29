# Ranking Input Migration — v1.3.0 to v1.3.1

## Frozen baseline
The v1.3.0 schema and alias registry remain unchanged and authoritative for v1.3.0 workbooks.

## Local schema registry
The v1.3.1 schema resolves frozen v1.3.0 row definitions through `urn:aipc:minimum-workbook:1.3.0`, registered to the frozen local schema file. Network resolution is prohibited. CI must prove that RFQ, history and metadata rows validate through this local registry.

## v1.3.0 behaviour
Existing workbooks remain readable and reviewable. They remain analytically blocked by `GOVERNED_RANKING_INPUTS_NOT_CANONICAL`.

## v1.3.1 behaviour
The fourth sheet is optional for review intake but mandatory for future governed analytical candidacy. A v1.3.1 workbook without `SUPPLIER_RANKING_INPUTS` receives `SUPPLIER_RANKING_INPUTS_SHEET_MISSING` and remains review-only.

## Source evidence boundary
A source workbook may optionally provide `SOURCE_EVIDENCE_STATUS`, but it is non-authoritative. Build C2 must derive per-field canonical evidence status. Source rows must provide per-field `VALUE_ORIGINS`; engine defaults are prohibited.

## No silent upgrade
The system must not infer v1.3.1 from column presence, rewrite metadata, reuse ignored v1.3.0 columns as canonical values, inherit mapping confirmations across schema/registry versions, or trust source-declared validity as canonical validity.

## Explicit migration steps
1. Set workbook schema version to 1.3.1.
2. Add and populate `SUPPLIER_RANKING_INPUTS`.
3. Regenerate source-file hash.
4. Validate through the local 1.3.0/1.3.1 schema registry.
5. Confirm every listed non-canonical ranking alias and detected scale; unlisted fields require exact canonical headers.
6. Recompute per-field canonical evidence status, freshness and scope applicability in Build C2.
7. Retain Build E review-only behaviour until a separate E2 authorization.

## Enforcement boundary
JSON Schema enforces structure, numeric ranges, scope combinations, evidence presence, per-field origins, closed fields and SHA-256 format. Build C2 enforces semantic scale ambiguity, mode eligibility, freshness, scope matching and cross-row findings. Documentary policy defines metric meaning and approved evidence expectations.

## Compatibility boundary
B2 and C2 completion alone must not remove `GOVERNED_RANKING_INPUTS_NOT_CANONICAL`, create an analytical DataFrame, or enable scoring.
