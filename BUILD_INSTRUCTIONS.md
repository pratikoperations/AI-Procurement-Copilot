# Build Instructions

## Purpose

This file explains how to resume and continue the project if chat history is lost.

## Recovery Start Point

Always begin by reading these files in order:

1. `PROJECT_STATUS.md`
2. `VERSION_MANIFEST.md`
3. `BUILD_HISTORY.md`
4. `CHANGELOG.md`
5. `DECISION_LOG.md`
6. `ROADMAP.md`
7. `ARCHITECTURE.md`
8. `PROJECT_BUILD_PLAN.md`

## Build Rules

1. GitHub is the canonical source of truth.
2. No major work should exist only in chat.
3. Every meaningful milestone must be committed.
4. Each milestone should update project status, changelog, and build history.
5. Major decisions must be recorded in the decision log.
6. The app should remain runnable after each completed build milestone.
7. Build in logical batches, not massive single updates.

## Development Sequence

```text
Plan architecture
Design/update folder structure
Generate or update code
Validate logic
Update documentation
Commit to GitHub
Update build status
Proceed to next batch
```

## Local Run Command

After application code is added:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Current Build

Build 0.1 — Repository Foundation

## Next Build

Build 0.2 — Streamlit Framework and Modular Application Skeleton
