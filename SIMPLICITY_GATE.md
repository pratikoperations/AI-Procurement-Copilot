# Simplicity Gate

## Purpose

The simplicity gate prevents accidental complexity without weakening essential procurement, engineering, assurance or recovery controls. Every material feature, abstraction, adapter, integration or governance artefact should receive one decision: `APPROVE`, `SIMPLIFY`, `DEFER` or `REJECT`.

## Evaluation Sequence

### 1. Define the Need

- What procurement, governance, reliability or interview problem is being solved?
- What observable outcome will prove value?
- What happens if the change is not made?
- Is the risk material enough to justify repository change?

### 2. Check Existing Capability

- Does an existing engine, module, contract, document or test already perform the function?
- Can the requirement be met by extending or referencing existing authority?
- Would the proposal create a second source of truth or calculation path?
- Are there at least two real consumers for a new abstraction?

### 3. Separate Accidental and Essential Complexity

#### Accidental complexity to reduce

- duplicate logic;
- unnecessary adapters;
- overlapping validation;
- speculative abstractions;
- unused configuration;
- redundant documentation;
- parallel implementations of the same rule;
- copied formulas that can drift from executable logic;
- compatibility layers with no defined retirement or benchmark purpose;
- configuration options unsupported by current business use.

#### Essential controls to preserve

- business-rule traceability;
- assumption provenance;
- risk-based tests;
- architecture separation;
- calculation evidence and reconciliation;
- validation and fail-closed behaviour;
- immutable contracts where justified;
- deterministic output;
- exact SHA and recovery records;
- human procurement review and approval;
- portfolio-versus-production boundaries;
- category-specific rules that cannot safely be generalized.

### 4. Select the Minimum Safe Design

Prefer the smallest change that:

- preserves one authoritative business-rule path;
- remains isolated until accepted;
- supports deterministic verification;
- keeps rollback to one branch, PR or merge revert;
- does not pre-build speculative production infrastructure;
- exposes limitations rather than hiding missing evidence.

## Decision Outcomes

### APPROVE

Use when:

- the need is material and evidenced;
- no existing authority already solves it;
- the design is bounded;
- essential controls remain intact;
- maintenance and rollback are proportionate.

### SIMPLIFY

Use when:

- the need is valid;
- the proposed design contains avoidable layers, duplication, options or documentation;
- a smaller implementation can deliver the same controlled result.

The approval must state what is removed or reduced before implementation.

### DEFER

Use when:

- potential value exists but dependency, data, evidence, maturity or adoption is insufficient;
- the feature is not needed for the current interview or business outcome;
- implementation now would create speculative architecture.

Deferral must record the trigger that would justify reconsideration.

### REJECT

Use when the proposal:

- creates a second business-rule authority;
- duplicates allocation, scoring, eligibility or calculation logic;
- infers missing technical eligibility or supplier capacity;
- mixes presentation code with authoritative calculations;
- weakens provenance, traceability, validation or human approval;
- adds production infrastructure only for portfolio appearance;
- reduces tests only to improve speed or reported test count;
- replaces immutable evidence with narrative documentation;
- creates parallel current-state documents;
- cannot be rolled back or verified proportionately.

## Required Decision Record

For each material proposal record:

- proposal;
- business value;
- affected authority;
- existing capability checked;
- accidental complexity identified;
- essential controls preserved;
- minimum safe design;
- decision;
- reasons;
- implementation boundary;
- verification required;
- deferral/review trigger where applicable.

## Examples

### New allocation algorithm

`REJECT` if it independently calculates the same sourcing event as the accepted Gate 2 engine. `SIMPLIFY` to a category adapter or compatibility benchmark if a genuine category-specific rule must be preserved.

### New project-status document

`REJECT` when it duplicates `PROJECT_CONTROL.md`. `APPROVE` only if it is a historical closure record with a distinct purpose and immutable evidence basis.

### Production authentication for an interview showcase

`DEFER` unless a real deployment, security or client requirement exists. Do not add it solely to claim enterprise readiness.

### Additional validation

`APPROVE` when it prevents a material business failure and does not duplicate an existing validator. Validation is essential complexity when it protects authoritative decisions.
