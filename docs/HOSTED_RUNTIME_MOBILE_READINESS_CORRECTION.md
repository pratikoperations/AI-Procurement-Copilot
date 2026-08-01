# Hosted Runtime and Mobile Readiness Correction

## Governed scope

- Base main SHA: `d143b9f108655732ac1db8988959d51e3c39ae6c`
- Superseding branch: `fix/hosted-runtime-mobile-readiness`
- Existing verification PR: `#35`
- Superseded narrow styling PR: `#36`

## Confirmed hosted findings

1. `C3-RUNTIME-01`: Steel reached the generic scenario engine and raised a `KeyError` before its governed Steel dashboard could render.
2. `MOBILE-UX-02`: BaseWeb normal focus still showed a red border and clipped yellow marker on Android.
3. `MOBILE-UX-01`: metric columns remained compressed instead of stacking on narrow screens.
4. `MOBILE-OVERFLOW-01`: page-level horizontal overflow remained visible.
5. `LANDING-UX-01`: the hosted screenshot appeared to repeat the no-live-ERP card; repository source contains one card, so the correction treats this as a rendering symptom rather than deleting valid content.
6. `LOG-TECH-01`: Streamlit cache hashing falls back to pickling for list-valued DataFrame/Series cells. This is retained as non-blocking technical debt because the fallback does not cause the Steel crash and normalization could alter governed evidence structures.

## Correction architecture

- The existing tested PR #36 focus work is preserved as the branch starting point.
- `run_scenario_table` applies final hosted-browser presentation overrides for all standard category routes.
- Steel is detected before generic scenario construction and dispatched to `render_steel_governed_dashboard`.
- The governed Steel dashboard renders its own seven scenarios, allocations and exports, then terminates the Streamlit run.
- C1 and C2 continue through their existing category-aware scenario paths.
- Streamlit 1.59.1 selectors target both BaseWeb wrappers and the actual combobox focus, expanded and invalid states.
- Narrow screens force Streamlit columns into a vertical flow and retain internal table scrolling.

## Exclusions

No category calculation, supplier data, Steel scoring, Steel scenario definition, allocation algorithm or export schema was changed. No production deployment, tag, release, merge or branch deletion was performed.

## Remaining verification

A hosted preview must confirm:

- Steel renders without the generic `KeyError`;
- Steel-specific suppliers, scenarios, allocations and downloads appear;
- select focus shows one blue ring and no red/yellow normal-focus treatment;
- metric cards stack and remain readable;
- page-level overflow is absent while tables retain internal scrolling;
- desktop keyboard interaction remains usable.
