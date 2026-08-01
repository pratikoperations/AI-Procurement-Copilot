# EAS-BIV Final Closure Record

## Programme

**Explainability, Assumption Provenance and SourceMate — Basic Interview Version**

## Programme objective

Create a governed, read-only explanation and evidence layer around the existing procurement decision-support services without replacing authoritative calculations, reconstructing unavailable evidence or enabling autonomous procurement decisions.

## Closure baseline

- Gate 5 starting baseline / Gate 4 merged baseline SHA: `834b34db145cc0156196579f7419e7db7b438106`
- Merged Gate 4 PR: `#42`
- Gate 4 accepted head SHA: `cbc4652290dbf5c7579cce7b30d37ee64bc7a225`
- Gate 4 merge commit: `834b34db145cc0156196579f7419e7db7b438106`
- Accepted CI: Quality Checks run `816`
- Run ID: `30706340753`
- Job ID: `91386012618`
- Python: `3.11.15`
- Tests: `1011 passed`, `0 failures`, `0 errors`
- Python compilation: passed
- Streamlit smoke: passed
- Warning boundary: one pre-existing pandas `FutureWarning`; no new Gate 4 warning

This SHA is the pre-Gate 5 baseline, not the final frozen Gate 5 main SHA. The final resulting main SHA is recorded in the governed post-merge verification and final-freeze declaration so this closure record remains valid without a second documentation PR.

## Gate capability summary

### Gate 1A — catalogue and provenance

- stable calculation, formula and assumption identities;
- supplied, defaulted, inferred and derived provenance;
- read-only Explorer payloads;
- formula metadata retained as documentation only.

### Gate 2 — governed traces

- deterministic trace identity;
- normalized inputs and authoritative outputs;
- parameter-precedence evidence;
- retained configuration versions;
- mandatory human review.

### Gate 3 — reconciliation and evidence assurance

- exact, tolerated, mismatch and unavailable-evidence classifications;
- fail-closed defect classifications;
- export evidence registry and assurance;
- explicit adapter-backed and deferred coverage.

### Gate 4 — presentation and SourceMate

- `AIPC-GOVERNED-EXPLORER-1.0`;
- `AIPC-SOURCEMATE-BASIC-1.0`;
- read-only Overview, Assumptions, Calculation Trace, Reconciliation, SourceMate and Human Review sections;
- evidence-derived checklist statuses;
- explicit unavailable configuration-version disclosure;
- controlled cross-category demonstration routes.

## Final architecture

```text
Existing authoritative procurement services
        |
Calculation catalogue and assumption provenance
        |
Deterministic governed traces
        |
Reconciliation and export evidence assurance
        |
Governed Calculation Explorer and SourceMate Basic
        |
Read-only human review and interview evidence
```

The architecture is an assurance and presentation layer. It does not create a second calculation engine.

## Contract versions

- Calculation trace: `AIPC-CALC-TRACE-1.0`
- Governed Explorer: `AIPC-GOVERNED-EXPLORER-1.0`
- SourceMate Basic: `AIPC-SOURCEMATE-BASIC-1.0`

## Adapter-backed coverage

The dedicated adapter-backed set remains exactly:

- `REC-PET`
- `REC-KRF`
- `REC-COR`
- `REC-LAM`
- `REC-STL`
- `REC-SCORE-GEN`
- `REC-ELG`

## Deferred coverage

All remaining non-export routes remain `unsupported_deferred_coverage`.

Deferred routes may execute their existing authoritative service but are not represented as adapter-reconciled. The application must not fabricate traces, intermediates or reconciliation evidence for those routes.

## Governance controls

1. Existing business services remain authoritative.
2. Formula metadata is documentation only and is never executed.
3. The Explorer does not reproduce business calculations.
4. Unavailable evidence is disclosed and is never inferred or reconstructed.
5. SourceMate presents registered internal evidence locations and does not perform external verification.
6. Evidence registration does not prove runtime presence in every export package.
7. Deferred routes are not adapter-reconciled.
8. No autonomous recommendation, award or production allocation is performed.
9. No approval persistence or workflow write-back exists.
10. Human procurement review and approval remain mandatory.
11. Demonstrations must use synthetic or sanitized data.
12. Illustrative outputs are not realized-savings evidence.

## Supported claims

The completed BIV supports claims that the project:

- provides governed procurement decision support;
- exposes calculation metadata and authoritative source functions;
- classifies assumption provenance;
- retains deterministic trace and configuration identity;
- reconciles supported adapter-backed routes;
- presents internal evidence locations and limitations;
- discloses deferred coverage rather than hiding it;
- maintains mandatory human-review boundaries;
- is protected by automated regression, compilation and startup checks.

## Unsupported claims

The completed BIV does not prove:

- production readiness;
- live SAP or Oracle integration;
- enterprise security or scale;
- universal category or ERP compatibility;
- external evidence verification;
- physical supplier audits or legal validation;
- realized savings from organizational use;
- autonomous supplier recommendation, approval or award;
- approval persistence or ERP write-back;
- formal browser-device or WCAG certification.

## Automated, source-level and manual evidence

### Automated evidence

- full regression suite;
- Python compilation;
- Streamlit startup smoke;
- deterministic trace and reconciliation tests;
- documentation and governance contract tests.

### Source-level evidence

- contract constants and presenter boundaries;
- absence of formula execution and prohibited UI controls;
- retained configuration versions;
- evidence-derived checklist statuses;
- explicit deferred-route handling.

### Physical browser and device evidence

Physical browser and device observations are not inferred from automated tests. Unless separately supplied and recorded, every item below remains `not performed`.

| Manual observation | Status | Evidence/reference |
|---|---|---|
| Desktop hosted load | not performed | No physical browser evidence supplied |
| Narrow desktop viewport | not performed | No physical browser evidence supplied |
| Android portrait | not performed | No Android evidence supplied |
| Android landscape | not performed | No Android evidence supplied |
| Explorer navigation | not performed | No physical interaction evidence supplied |
| Overview section | not performed | No physical interaction evidence supplied |
| Assumptions section | not performed | No physical interaction evidence supplied |
| Calculation Trace section | not performed | No physical interaction evidence supplied |
| Reconciliation section | not performed | No physical interaction evidence supplied |
| SourceMate section | not performed | No physical interaction evidence supplied |
| Human Review section | not performed | No physical interaction evidence supplied |
| Packaging TCO deferred state | not performed | No physical interaction evidence supplied |

## Remaining limitations

- SourceMate does not independently generate or externally verify evidence.
- Runtime evidence presence defaults to not independently checked in the Explorer.
- Fourteen non-export routes remain deferred.
- Generic scoring and eligibility are adapter-backed but not primary hosted demonstration routes.
- Streamlit smoke is startup evidence, not browser interaction evidence.
- Mobile behavior is not physically certified.
- Human-review status is read-only and is not persisted.
- Some technical evidence remains displayed in expandable JSON structures.

## Final-freeze SHA recording

The merge commit created when the governed Gate 5 PR enters `main` is the final resulting main SHA. That SHA is captured in the governed post-merge verification and final-freeze declaration together with the merged PR state, exact file boundary, CI result and retained-governance checks. The declaration is the authoritative freeze record; this repository document intentionally records the pre-merge Gate 5 baseline.

## Final freeze criteria

The programme may be declared frozen when:

1. Gate 5 documentation is governed, CI-validated and merged.
2. The final resulting main SHA is captured in the governed post-merge verification and final-freeze declaration.
3. All closure documents use consistent contract, CI and coverage facts.
4. No unsupported hosted, external-verification, production or realized-savings claim remains.
5. Manual browser/device items are either evidenced as passed/failed or remain explicitly `not performed`.
6. PR #1 and retained governance branches remain preserved.
7. No deferred adapter, production change, tag or release is added without separate authorization.

## Post-BIV backlog

Potential post-BIV work, requiring separate planning and authorization:

1. Packaging TCO adapter;
2. raw-material TCO adapter;
3. generic scenario trace adapter;
4. standard and optimized allocation adapters;
5. category-specific scenario adapters;
6. browser automation for the Explorer route;
7. physical Android and desktop validation;
8. optional approval workflow only under enterprise-grade governance.

## Closure position

Gate 5 is documentation and assurance closure only. It does not modify production application functionality, business calculations, recommendations, allocations, exports or schemas.
