# AI Procurement Copilot — Test Evidence

## Quality approach

The repository uses automated checks to protect procurement calculations, validation controls, export integrity, UI contracts, governed explainability contracts, ERP Preview boundaries and application startup.

## Covered areas

- Python compilation
- Procurement-engine regression tests
- Currency and unit integrity
- Category-specific logic
- Business-rule and recommendation eligibility
- Adversarial and external-file validation
- Supplier Intelligence and UI contracts
- Business-readable and machine-readable exports
- ERP schema, mapping, loader and structural validation
- ERP Upload Preview presenter and page smoke
- Calculation catalogue and assumption provenance
- Parameter precedence and deterministic trace identity
- Reconciliation and export evidence assurance
- Governed Calculation Explorer and SourceMate Basic contracts
- Public presentation and release-version assertions
- Canonical Streamlit startup smoke

## Historical build evidence

### Build Group A

Approved head: `8b113a195e5a742c6bf2fe2785d79390de8ce17a`

Quality Checks run 453 passed dependency installation, compilation, the complete regression suite and canonical Streamlit smoke.

### Build Group B

Approved head: `a5e4c97fb42af134bced25706b8f1dc7e12a0971`

Quality Checks run 465, run ID `30247178739`, passed dependency installation, Python compilation, the complete regression suite and canonical Streamlit smoke with 0 failures.

### Build Group C

Owner-review candidate head before evidence refresh: `5cad387b457720fa5decf89e42882463a9ad0ea8`

Quality Checks run 484, run ID `30249982994`, passed dependency installation, compilation, the complete regression suite and canonical Streamlit smoke.

## EAS-BIV Gate evidence

### Gate 1A — Calculation catalogue and assumption provenance

PR `#39` added stable calculation/assumption identities, provenance classifications and a read-only normalized Explorer foundation while keeping formula text non-executable.

### Gate 2 — Governed traces

PR `#40` added governed parameter precedence, deterministic trace identity and representative read-only adapters.

### Gate 3 — Reconciliation and evidence assurance

PR `#41` added cross-category reconciliation classifications, fail-closed mismatch handling, coverage registration and export evidence assurance.

### Gate 4 — Governed Explorer and SourceMate Basic

PR `#42` merged as `834b34db145cc0156196579f7419e7db7b438106` and added:

- `AIPC-GOVERNED-EXPLORER-1.0`;
- `AIPC-SOURCEMATE-BASIC-1.0`;
- retained `configuration_versions` in `AIPC-CALC-TRACE-1.0`;
- evidence-derived human-review checklist states;
- explicit deferred-route and unavailable-evidence presentation.

## Accepted Gate 4 validation

- authoritative main SHA: `834b34db145cc0156196579f7419e7db7b438106`;
- Quality Checks run: `816`;
- run ID: `30706340753`;
- job ID: `91386012618`;
- Python: `3.11.15`;
- tests: `1011 passed`;
- failures: `0`;
- errors: `0`;
- Python compilation: passed;
- Streamlit smoke: passed;
- one pre-existing pandas `FutureWarning` remained;
- no new Gate 4 warning was introduced.

## Evidence classification

### Automated evidence

Automated evidence proves that the tested repository revision:

- compiles;
- passes the complete regression suite;
- starts through the canonical Streamlit smoke path;
- preserves deterministic trace and reconciliation contracts;
- enforces documentation and UI boundary assertions.

### Source-level evidence

Source review and contract tests verify:

- formula metadata is not executed;
- authoritative business services remain primary;
- configuration versions are retained;
- checklist states derive from available evidence;
- deferred routes are not given fabricated traces;
- SourceMate does not implement external retrieval or verification;
- prohibited approval and award controls are absent from the Gate 4 UI.

### Physical browser and device evidence

Automated and source-level evidence do not prove:

- pixel-level rendering;
- physical Android behavior;
- narrow-viewport usability;
- touch interaction;
- hosted route continuity;
- formal accessibility certification.

Unless a separate observed evidence record is supplied, physical desktop and mobile validation remains `not performed`.

## Warning boundary

The accepted baseline contains one pre-existing pandas `FutureWarning` in adversarial-input testing. Gate 5 does not fix or reclassify that warning. Existing GitHub Actions Node-version notices are also outside Gate 5 scope.

## Visual evidence boundaries

- SVG application views are illustrative and are not direct proof of the final hosted candidate.
- Streamlit smoke is startup evidence, not a browser interaction test.
- Manual browser/device observations must not be marked passed without actual evidence.
- Automated tests do not prove production security, enterprise scale, live ERP integration, external evidence verification or business adoption.

## Canonical closure sources

- [EAS-BIV Final Closure](EAS_BIV_FINAL_CLOSURE.md)
- [EAS-BIV Interview Evidence Pack](EAS_BIV_INTERVIEW_EVIDENCE_PACK.md)
- [Governance and Limitations](07_GOVERNANCE_AND_LIMITATIONS.md)
- [Demonstration Guide](08_DEMO_GUIDE.md)
