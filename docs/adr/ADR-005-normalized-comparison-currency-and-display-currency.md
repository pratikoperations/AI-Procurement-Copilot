# ADR-005 — Normalized Comparison Currency and Display Currency

## Status

Accepted for current portfolio architecture, subject to governed change control.

## Context

Supplier offers may originate in different currencies. Ranking and allocation require one deterministic comparison basis, while users may need outputs displayed in another currency.

## Decision

Comparison, scoring and ranking use the governed normalized currency basis produced by authoritative calculation logic. Display currency is presentation only.

Changing display currency must not alter supplier ranking, eligibility, allocation or canonical comparison values. FX assumptions require explicit provenance, deterministic application and consistent reuse. UI and export layers must consume canonical converted values and must not independently recalculate them.

## Decision Drivers

- Ensure like-for-like supplier comparison.
- Prevent display choices from changing business outcomes.
- Preserve FX assumption provenance.
- Keep calculation and presentation responsibilities separate.
- Support deterministic reconciliation across UI and exports.

## Considered Alternatives

- **Rank directly in supplier quote currencies:** rejected because values are not comparable.
- **Recalculate conversions in each view:** rejected due to drift and inconsistent rounding.
- **Allow display currency to drive engine inputs:** rejected because presentation would become authoritative.

## Consequences

Canonical values and FX evidence must be carried through governed contracts or result structures. Display layers may format or convert only when using an explicitly authorized presentation value that cannot affect decision logic. Rounding for display must not replace calculation precision.

## Risks and Controls

- **Risk:** stale or unsupported FX assumptions. **Control:** provenance, effective-date evidence and reverification triggers.
- **Risk:** UI conversion differs from engine conversion. **Control:** one authoritative normalized result.
- **Risk:** rounding changes rank. **Control:** rank on canonical values before display formatting.

## Scope

Cross-currency supplier comparison, scoring, ranking, allocation inputs, UI presentation and exports.

## Non-Scope

Selection of live FX providers, hedging policy or treasury accounting.

## Evidence

- `PROJECT_ARCHITECTURE.md`
- `BUSINESS_RULES.md`
- `FORMULA_TRACEABILITY_REGISTER.md`
- Relevant category cost and currency modules
- `modules/multi_supplier_allocation_adapter.py`
- Relevant currency and ranking tests
- Merged PR #47

## Reverification Triggers

Changes to normalized currency, FX source, effective-date treatment, conversion precision, rounding, ranking inputs, display-currency controls or export currency behaviour.