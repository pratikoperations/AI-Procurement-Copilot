# Build 0.9.3.1 Hotfix

## Incident

The deployed Streamlit app failed at startup with:

`KeyError: 'category_profile'`

The app accessed `assumptions["category_profile"]` directly. During an inconsistent deployment state, the sidebar return contract did not provide that key.

## Root Cause

The integration between `render_sidebar()` and `app.py` relied on an unguarded dictionary key. Although the current sidebar implementation returned the key, the application had no fallback when metadata was missing or an older sidebar revision was briefly deployed.

## Resolution

- Added `DEFAULT_CATEGORY_PROFILE` in `modules/category_engine.py`.
- Added `ensure_category_profile()` to complete or safely replace missing metadata.
- Added `build_sidebar_result()` so every sidebar execution path returns `category_profile`.
- Updated `app.py` to use safe access and normalize the profile before rendering.
- Added regression tests for normal, partial, and missing profile cases.

## Validation Status

- Static integration: Complete
- Regression tests: Added
- Streamlit smoke test: Pending latest GitHub Actions result
- Live deployment validation: Pending

## Release Rule

Do not begin Build 0.9.4 until CI is green and the deployed app opens without the category-profile error.
