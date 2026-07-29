# AI Procurement Copilot v1.3 — Architecture Decision Records

## ADR-001 — One sourcing event per analysis

**Decision:** One analysis session evaluates one `SOURCING_EVENT_ID`. A workbook may be rejected or require event selection if it contains multiple events.

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
