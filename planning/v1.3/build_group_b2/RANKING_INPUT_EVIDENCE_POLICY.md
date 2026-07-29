# Ranking Input Evidence Policy — v1.3.1

## Principle
A ranking value is eligible only when its type, range, scope, scale, freshness, source and approval evidence are valid. User acknowledgement cannot convert invalid evidence into valid evidence.

## Source assertion versus canonical determination
`SOURCE_EVIDENCE_STATUS` is optional and non-authoritative. It records what the source claims. Build C2 must independently derive `CANONICAL_EVIDENCE_STATUS` for each canonical ranking field. A source claim of `VALID` never bypasses validation.

## Per-field result
The normative Build C2 output for each field contains canonical field, canonical value, canonical evidence status, value origin, source reference and validation findings. Mixed statuses and origins within one source row are allowed and expected.

## Freshness
### Quick RFQ
- OTIF, PPM, complaint rate and capacity buffer: maximum age 12 months.
- Audit score: maximum age 24 months.
- Recyclability: maximum age 24 months.
- Certification: valid on evaluation date.
- Carbon, EPR and PCR when supplied: maximum age 24 months.

### Full Sourcing Review
- OTIF, PPM, complaint rate and capacity buffer: maximum age 12 months.
- Audit score: maximum age 24 months.
- Recyclability: maximum age 24 months.
- Certification: valid on evaluation date.
- Carbon score: maximum age 24 months.
- EPR readiness: maximum age 12 months.
- PCR evidence: maximum age 24 months.

## Required evidence
Measured performance metrics require a source system/report, measurement period and record count. Audit score requires audit date, standard and reference. Certification score requires type, issuer, reference and validity dates. Carbon score requires method and reference. EPR readiness requires jurisdiction and reference. PCR content requires verification method and reference.

## Canonical status model
- `VALID`: all controls pass.
- `MISSING`: value or mandatory evidence absent.
- `INVALID_TYPE`: canonical type cannot be established.
- `OUT_OF_RANGE`: numeric bounds fail.
- `STALE`: evidence exceeds freshness policy.
- `AMBIGUOUS_SCOPE`: supplier/category applicability is unclear.
- `AMBIGUOUS_SCALE`: percentage or score scale is uncertain.
- `CONTRADICTORY`: competing records at equal precedence disagree.
- `UNVERIFIED`: source or approval evidence is insufficient.

## Rule ownership
- `JSON_SCHEMA_ENFORCED`: row structure, ranges, scope field constraints, supporting evidence presence, per-field origins, additional properties and SHA-256 format.
- `BUILD_C2_ENFORCED`: freshness, semantic scale ambiguity, mode eligibility, scope matching, duplicate/contradiction/overlap and canonical status derivation.
- `DOCUMENTARY_POLICY`: metric semantics and approved evidence expectations.

## Findings
- `RANKING_INPUT_SCALE_AMBIGUOUS`: Blocking.
- `RANKING_SCOPE_AMBIGUOUS`: Blocking.
- `PERFORMANCE_INPUT_STALE`: Blocking when mandatory.
- `AUDIT_EVIDENCE_STALE`: Blocking when mandatory.
- `CERTIFICATION_EXPIRED`: Blocking.
- `ESG_INPUT_STALE`: Blocking when mandatory.
- `MEASUREMENT_PERIOD_INVALID`: Fatal.
- `CONTRADICTORY_RANKING_INPUT`: Fatal.
- `OVERLAPPING_RANKING_MEASUREMENT_PERIOD`: Blocking.
- `EXACT_RANKING_INPUT_DUPLICATE`: Information.

## Derivation
Derived values must retain derivation method/version, source rows and source-file hash. OTIF may be derived from governed on-time and in-full history. PPM must not be derived without a governed denominator. Engine defaults are never valid evidence.
