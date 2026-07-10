# GitHub Project Operating Standard

## Purpose

This document defines how the AI Procurement Copilot project will be built and governed.

## Master Rule

GitHub is the single source of truth for this project.

## Required Practice

Every meaningful build action must be committed to GitHub.

## Required Files to Maintain

- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `BUILD_HISTORY.md`
- `DECISION_LOG.md`
- `VERSION_MANIFEST.md`
- `RECOVERY_MANIFEST.md`

## Commit Standard

Each milestone should include:

1. Source code changes
2. Documentation updates
3. Project status update
4. Changelog update
5. Build history update
6. Decision log update if a decision changed

## Build Batch Rule

Do not attempt massive untracked changes. Build in small, recoverable batches.

## App Stability Rule

After each completed build milestone, the application should remain runnable unless the milestone is explicitly marked as architecture-only.

## Recovery Rule

If chat context is lost, resume from GitHub by reading the recovery files.

## AI Usage Rule

AI may assist with drafting, explanation, classification, code generation, summarization, and scenario reasoning. AI must not hide procurement decision logic or make unexplainable award decisions.
