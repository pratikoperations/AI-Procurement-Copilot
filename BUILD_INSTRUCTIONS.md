# Build Instructions

## Purpose

This file is the mandatory starting point for every future build session. The project must be resumable from GitHub without relying on prior chat context.

## Session Start Checklist

1. Open `PROJECT_STATUS.md`.
2. Open `docs/MASTER_BUILD_ARCHITECTURE.md`.
3. Open `RECOVERY_MANIFEST.md`.
4. Read the latest entries in `ACTIVITY_LOG.md`, `BUILD_HISTORY.md`, `DECISION_LOG.md`, and `CHANGELOG.md`.
5. Read the latest build-specific QA report.
6. Verify the default branch, working branch, latest commit, current build number, and unresolved CI or validation items.
7. Confirm the exact acceptance criteria for the next build unit.

## Build Execution Standard

- Work in one coherent build unit at a time.
- Preserve existing functionality unless the build explicitly replaces it.
- Keep deterministic calculations separate from AI-generated text.
- Add or update tests with every logic change.
- Do not silently change business assumptions, scoring weights, units, thresholds, or defaults.
- Record material design decisions in `DECISION_LOG.md`.
- Record all build activity in `ACTIVITY_LOG.md`.

## Commit Standard

After every meaningful update:

1. Run applicable tests and checks.
2. Inspect the changed files and full diff.
3. Update mandatory governance files.
4. Commit using: `Build <ID>: <concise outcome>`.
5. Push the branch.
6. Re-fetch or inspect the GitHub commit to confirm the intended files are present.
7. Check CI status when applicable.
8. Store the QA result in GitHub.

A local or chat-only update is not considered complete.

## Mandatory Quality Check

Each update must record:

- Scope tested
- Tests run
- Result
- Known limitations
- Regression status
- CI status
- Reviewer or validation status
- Next action

## Completion Rule

A build is complete only when:

- Acceptance criteria are met
- Tests pass
- Documentation is synchronized
- Recovery documentation is current
- GitHub contains the committed implementation and QA evidence
- The repository can independently explain what changed, why, and what comes next

## Failure and Recovery Rule

If a build fails or remains incomplete:

- Do not overwrite the previous stable state.
- Record the failure in `ACTIVITY_LOG.md` and the build QA report.
- Record the last known good commit in `RECOVERY_MANIFEST.md`.
- Create a corrective build ID rather than hiding or deleting the failed attempt.

## Source-of-Truth Rule

When chat content conflicts with GitHub, the latest quality-checked GitHub record governs unless a new explicit decision is committed to the repository.

## Current Position

- Current build: Build 0.9.5 — Supplier Intelligence Platform
- Pending gate: CI and live Supplier Intelligence validation
- Next controlled expansion after Portfolio Edition v1.0 hardening: Packaging Value Engineering Scope A
