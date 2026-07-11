# Recovery Manifest

## Purpose

This file makes the project recoverable from GitHub alone. Chat history must not be required to understand the current state or continue the next build.

## Current Project Identity

- Project: AI Procurement Copilot
- Integrated specialist module: Packaging Value Engineering & Decision Intelligence
- Edition: Portfolio Edition v1.0
- Current Build: Build 0.9.5 — Supplier Intelligence Platform
- Current Status: Build completed; CI and live Supplier Intelligence validation pending
- Canonical Repository: `pratikoperations/AI-Procurement-Copilot`
- Stable branch: `main`
- Architecture branch: `agent/finalize-build-architecture`

## Last Known Stable Point

- Main commit before architecture branch: `5da64214b1c8a487f919a3dbc9f86730e29c5881`
- Message: `Build 0.9.5: update interview guide`
- Do not begin Packaging Value Engineering implementation until Build 0.9.5 CI and live validation are closed and Portfolio Edition v1.0 is hardened.

## Mandatory Recovery Reading Order

1. `PROJECT_STATUS.md`
2. `docs/MASTER_BUILD_ARCHITECTURE.md`
3. `BUILD_INSTRUCTIONS.md`
4. `ACTIVITY_LOG.md`
5. `VERSION_MANIFEST.md`
6. `BUILD_HISTORY.md`
7. `CHANGELOG.md`
8. `DECISION_LOG.md`
9. Latest build-specific QA report in `docs/`
10. `ROADMAP.md` and `PROJECT_BUILD_PLAN.md`

## Core Recovery Files

- `README.md` — project overview
- `PROJECT_STATUS.md` — current build state and immediate next gate
- `docs/MASTER_BUILD_ARCHITECTURE.md` — integrated product architecture and all scope options
- `BUILD_INSTRUCTIONS.md` — mandatory session, commit, QA, and recovery workflow
- `ACTIVITY_LOG.md` — chronological build-session activity
- `VERSION_MANIFEST.md` — current version and build
- `BUILD_HISTORY.md` — completed build outcomes
- `CHANGELOG.md` — versioned changes
- `DECISION_LOG.md` — frozen architectural and business decisions
- `QUALITY_ASSURANCE_PROTOCOL.md` — QA standard
- Latest build QA report — actual evidence for the current milestone
- `ROADMAP.md` — future milestones
- `PROJECT_BUILD_PLAN.md` — detailed build plan

## Recovery Procedure

1. Open the canonical GitHub repository.
2. Confirm the latest commit and branch.
3. Read the mandatory files in the order above.
4. Identify the current build, pending gate, last known stable commit, and next approved scope.
5. Review open pull requests, failed CI, and unresolved QA items.
6. Resume only the next incomplete build unit.
7. After implementation, run tests, update governance records, commit, push, verify GitHub, and record QA evidence.

## Recovery Principles

- No important logic, decision, plan, build status, or validation evidence may exist only in a ChatGPT conversation.
- GitHub governs when chat and repository records conflict.
- Failed attempts remain visible through logs and corrective builds.
- The previous stable state must remain recoverable.
- Packaging Value Engineering remains a module within AI Procurement Copilot, not a separate product or repository.
