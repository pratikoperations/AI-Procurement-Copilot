# Build 0.9.3.1 Hotfix

## Incident

The deployed Streamlit app failed at startup with:

`KeyError: 'category_profile'`

The app accessed `assumptions["category_profile"]` directly. During an inconsistent deployment state, the sidebar return contract did not provide that key.

## Root Cause

The integration between `render_sidebar()` and `app.py` relied on an unguarded dictionary key. Although the current sidebar implementation returned the key, the application had no fallback when metadata was missing or an older sidebar revision was briefly deployed.

A follow-up regression test then exposed a second merge defect: an explicit raw-material `unit="kg"` was preserved, but the default `units=["piece"]` value remained because `setdefault()` treated the default key as already populated.

## Resolution

- Added `DEFAULT_CATEGORY_PROFILE` in `modules/category_engine.py`.
- Added `ensure_category_profile()` to complete or safely replace missing metadata.
- Added `build_sidebar_result()` so every sidebar execution path returns `category_profile`.
- Updated `app.py` to use safe access and normalize the profile before rendering.
- Added regression tests for normal, partial, and missing profile cases.
- Corrected singular/plural unit reconciliation so explicit `unit` or `units` values always override defaults.

## Regression Fix

The profile merge now:

1. Copies the default profile.
2. Applies all explicitly supplied profile values.
3. Derives `units` from an explicit `unit` only when `units` was not supplied.
4. Derives `unit` from explicit `units` only when `unit` was not supplied.
5. Never allows the packaging default `piece` unit to overwrite an explicit raw-material unit such as `kg`.

Expected regression result after this fix:

- 28 tests passed
- 0 tests failed
- Streamlit smoke test executed

## Validation Status

- Static integration: Complete
- Regression fix: Committed
- GitHub Actions: Pending latest run
- Streamlit smoke test: Pending latest workflow result
- Live deployment validation: Pending

## Release Rule

Do not begin Build 0.9.4 until CI is green and the deployed app opens without the category-profile error.
