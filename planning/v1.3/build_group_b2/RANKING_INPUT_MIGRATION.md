# Ranking Input Migration — v1.3.0 to v1.3.1

## Frozen baseline
The v1.3.0 schema and alias registry remain unchanged and authoritative for v1.3.0 workbooks.

## v1.3.0 behaviour
Existing workbooks remain readable and reviewable. They remain analytically blocked by `GOVERNED_RANKING_INPUTS_NOT_CANONICAL`.

## v1.3.1 behaviour
The fourth sheet is optional for review intake but mandatory for future governed analytical candidacy. A v1.3.1 workbook without `SUPPLIER_RANKING_INPUTS` receives `SUPPLIER_RANKING_INPUTS_SHEET_MISSING` and remains review-only.

## No silent upgrade
The system must not infer v1.3.1 from column presence, rewrite metadata, reuse ignored v1.3.0 columns as canonical values, or inherit mapping confirmations across schema/registry versions.

## Explicit migration steps
1. Set workbook schema version to 1.3.1.
2. Add and populate `SUPPLIER_RANKING_INPUTS`.
3. Regenerate source-file hash.
4. Validate the 1.3.1 schema and alias registry.
5. Confirm every non-canonical ranking alias and detected scale.
6. Recompute evidence status, freshness and scope applicability.
7. Retain Build E review-only behaviour until a separate E2 authorization.

## Compatibility boundary
B2 and C2 completion alone must not remove `GOVERNED_RANKING_INPUTS_NOT_CANONICAL`, create an analytical DataFrame, or enable scoring.