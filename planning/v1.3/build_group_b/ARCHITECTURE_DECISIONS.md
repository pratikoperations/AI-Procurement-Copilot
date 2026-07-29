# AI Procurement Copilot v1.3 — Architecture Decision Records

## ADR-001 — One sourcing event per analysis

**Decision:** One analysis session evaluates one `SOURCING_EVENT_ID`. A workbook may contain multiple events only when the user explicitly selects exactly one `SOURCING_EVENT_ID` before analysis. Cross-event combined analysis is prohibited.

**Reason:** Prevents cross-event supplier, quantity, currency and recommendation contamination.

## ADR-002 — Quotation-version selection

**Decision:** Preserve every version. The latest valid version is proposed, but unresolved status/date conflicts require explicit user confirmation. No version may silently overwrite another.

## ADR-003 — Comparison-currency precedence

**Decision:** Governed internal use uses `UPLOAD_METADATA.BASE_CURRENCY`. Portfolio mode may use an explicitly confirmed UI comparison currency. Exchange rates require value, date, policy source and provenance.

## ADR-004 — UOM conversion direction

**Decision:** `normalized_quantity = source_quantity × UOM_CONVERSION_FACTOR`, where the factor converts source UOM into `COMPARISON_UOM`. Price normalization must apply the inverse quantity relationship and preserve the original price basis.

## ADR-005 — Evidence-coverage denominator

**Decision:** The denominator contains approved applicable evidence dimensions, not all possible fields. Non-applicable dimensions are excluded; missing applicable dimensions reduce coverage.

## ADR-006 — History-matching hierarchy

**Decision:** Initial hierarchy:

1. exact supplier + material;
2. exact material across approved suppliers;
3. approved comparable group;
4. category-level;
5. unmatched.

Description-similarity matching is excluded from automatic use in Build Group B and requires future authorization.

## ADR-007 — Local/private storage scope

**Decision:** Build Group B defines storage requirements only. No persistence implementation is authorized. Future storage must be local or privately controlled, single-user, versioned, backup-capable and excluded from the public portfolio deployment.

## ADR-008 — Reference-snapshot scope

**Decision:** Initial snapshot families may include supplier display mapping, material/category mapping, UOM conversion, FX policy, scoring weights, PO history and supplier performance. Only approved immutable snapshots may support governed analysis. Build Group B creates no runtime snapshot store.

## ADR-009 — Hash identity and storage

**Decision:** `SOURCE_FILE_HASH_SHA256` records the original source export hash inside `UPLOAD_METADATA`. `UPLOAD_FILE_HASH_SHA256` is calculated after upload and stored in the external event/audit record, never inside the workbook it hashes.

## ADR-010 — Expired quotations

**Decision:** Expired quotations remain visible as blocked evidence but cannot support active comparison, recommendation language or award-oriented outputs.

## ADR-011 — Formula-cell policy

**Decision:** Formula cells in identity, quantity, price, currency, UOM, date, status, FX and key fields are rejected as Blocking or Fatal depending on whether valid rows remain. Formula cells in optional descriptive fields produce a Warning. Cached formula results are never silently treated as source values.

## ADR-012 — Tax comparability

**Decision:** Tax is excluded from comparable TCO by default. It may be included only when an approved policy classifies it as non-recoverable and comparable.

## ADR-013 — Historical staleness

**Decision:** Historical evidence older than 60 days from the approved evaluation date produces a Warning by default. An approved reference-data policy may override the threshold.
