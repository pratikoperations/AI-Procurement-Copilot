# ADR-007 — Assumption and Parameter Precedence

## Status

Accepted for current portfolio architecture, subject to governed change control.

## Context

The application can receive supplied values, governed workbook values, category defaults and controlled synthetic assumptions. Without explicit precedence and provenance, later integration may silently replace evidence or produce inconsistent outcomes.

## Decision

Assumption and parameter precedence must be explicit, deterministic and evidence-aware.

Supplied values, governed workbook values, category defaults and controlled synthetic assumptions remain distinguishable. Missing mandatory evidence must not be silently inferred. Assumptions require source, origin and applicable-scope provenance. UI, adapters and explanatory layers must not override the authoritative precedence defined by contracts, category authorities and governed controls.

Where a fixed source type has a governed evidence origin, contradictory origin claims must fail rather than relabel evidence. Category-adapter evidence requires explicit origin when no fixed inference is authorized.

## Decision Drivers

- Preserve assumption provenance.
- Prevent silent evidence substitution.
- Support deterministic scenario reproduction.
- Keep category and shared authorities aligned.
- Make synthetic, supplied and governed evidence visible to reviewers.

## Considered Alternatives

- **Last value wins:** rejected because order would silently determine business outcomes.
- **Treat all sources as equivalent:** rejected because evidence quality and authority differ.
- **Infer missing mandatory values:** rejected because missing evidence is not verified evidence.

## Consequences

Contracts and outputs must retain sufficient origin and precedence evidence. Integration layers may normalize supported representations but cannot change semantic authority. Contradictions or unsupported evidence may block readiness.

## Risks and Controls

- **Risk:** UI overrides an engine assumption. **Control:** route inputs through governed contracts and test precedence.
- **Risk:** synthetic evidence is presented as supplied. **Control:** explicit evidence origin and warning treatment.
- **Risk:** defaults conceal missing mandatory data. **Control:** reject or block where required evidence is absent.

## Scope

Input construction, source-origin handling, category defaults, scenarios, assumptions, adapters, UI controls and evidence presentation.

## Non-Scope

The numerical value of individual category formulas or detailed scenario catalogues.

## Evidence

- `PROJECT_CONTROL.md`
- `BUSINESS_RULES.md`
- `FORMULA_TRACEABILITY_REGISTER.md`
- `modules/allocation_contract.py`
- `modules/multi_supplier_allocation_adapter.py`
- Relevant provenance, missing-value and source-origin tests
- Merged PR #47

## Reverification Triggers

Changes to source types, evidence origins, precedence order, category defaults, workbook ingestion, synthetic data policy, missing-evidence treatment, UI overrides or scenario controls.