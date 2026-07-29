# Build Group E Rollback Plan

## Runtime disablement

`AIPC_GOVERNED_V13_ROUTE_ENABLED` is disabled by default. Enabled values are `1`, `true`, `yes`, and `on`. Missing, disabled or malformed values prevent Build C and Build D invocation while preserving demo and legacy routes. This build adds flag support only and does not change hosted environment settings.

## Application isolation

Governed-route exceptions return governed stop states and cannot fall through to synthetic or legacy data. Governed processing bypasses legacy fuzzy mapping and currency normalization.

## Code rollback

The Build Group E PR modifies only `app.py` and `modules/sidebar.py`; all other files are additive. The merge must remain independently revertible. No database, schema migration, deployment change, persistence or external integration is introduced.

## Reset rules

Upload, schema, alias registry, mapping, event, item, evaluation date, currency, findings or compatibility-manifest changes invalidate the current handoff confirmation.
