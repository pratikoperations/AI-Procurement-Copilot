# Master Build Architecture

## Architecture Decision

AI Procurement Copilot and Packaging Value Engineering & Decision Intelligence will use **separate GitHub repositories and separate file systems**.

This prevents duplicate file names, accidental overwrites, mixed build histories, unclear recovery states, and cross-project commits.

## Canonical Repositories

### Repository 1 — Existing

`pratikoperations/AI-Procurement-Copilot`

Owns:

- RFQ intelligence
- Procurement should-cost and TCO
- Supplier comparison and allocation
- Negotiation intelligence
- Supplier 360, performance, ESG, innovation, financial indicators, and SRM
- Procurement-level scenarios, executive recommendations, and savings tracking

### Repository 2 — To Be Created Before PVE Build

Recommended name:

`pratikoperations/Packaging-Value-Engineering-Decision-Intelligence`

Owns:

- Packaging baseline and specifications
- Packaging design alternatives
- Material and weight optimization
- Category-specific engineering should-cost
- Technical qualification
- Packaging quality and implementation risks
- Validation-test recommendations
- Sustainability indicators
- Risk-adjusted packaging recommendation
- Packaging trial and knowledge intelligence

Each repository is independently recoverable and contains its own code, data, tests, documentation, versions, activity log, QA reports, and release history.

## Integration Architecture

```text
Packaging Value Engineering Repository
│
│  exports a versioned Decision Package
│
▼
Integration Contract
│
▼
AI Procurement Copilot Repository
│
├── Supplier and RFQ Evaluation
├── TCO
├── Negotiation
├── Allocation
├── Executive Recommendation
└── Savings Realization
```

The projects integrate through explicit files or APIs, not shared writable folders.

## Integration Contract

PVE may export:

- `pve_decision_package.json`
- `pve_qualified_options.csv`
- `pve_target_costs.csv`
- `pve_validation_requirements.json`

Minimum fields:

- Decision package version
- Project and specification IDs
- Packaging category
- Baseline specification
- Approved or conditional alternatives
- Target cost
- Technical qualification status
- Risk-adjusted savings
- Confidence and data gaps
- Required validation
- Implementation constraints

The Procurement Copilot imports the package but does not alter the PVE source records.

## File-System Isolation Rules

- No code file is manually copied between repositories without a recorded decision.
- No repository writes directly into the other repository.
- Every file path is project-local.
- Each repository has its own `README.md`, `PROJECT_STATUS.md`, `BUILD_HISTORY.md`, `CHANGELOG.md`, `DECISION_LOG.md`, `ACTIVITY_LOG.md`, `VERSION_MANIFEST.md`, `RECOVERY_MANIFEST.md`, tests, and QA reports.
- Integration data lives only in a clearly named `integration/` directory in each repository.
- Imported packages are read-only inputs and include their source commit and schema version.

## PVE Repository Structure

```text
Packaging-Value-Engineering-Decision-Intelligence/
├── app.py
├── src/
│   ├── cost_engine/
│   ├── technical_qualification/
│   ├── risk_engine/
│   ├── sustainability/
│   ├── recommendation/
│   └── exports/
├── data/
│   ├── demo/
│   ├── schemas/
│   └── reference/
├── integration/
│   ├── contracts/
│   ├── exports/
│   └── samples/
├── tests/
├── docs/
│   ├── architecture/
│   ├── builds/
│   ├── qa/
│   └── demo/
├── README.md
├── PROJECT_STATUS.md
├── BUILD_INSTRUCTIONS.md
├── ACTIVITY_LOG.md
├── BUILD_HISTORY.md
├── CHANGELOG.md
├── DECISION_LOG.md
├── VERSION_MANIFEST.md
└── RECOVERY_MANIFEST.md
```

## Procurement Copilot Integration Structure

```text
AI-Procurement-Copilot/
├── integration/
│   └── packaging_value_engineering/
│       ├── contracts/
│       ├── imports/
│       ├── adapters/
│       └── tests/
└── existing procurement and supplier modules
```

## Scope Options for PVE

| Scope | Effort |
|---|---:|
| Lean Interview Project | 80–110 hours |
| Robust Interview Project | 150–200 cumulative hours |
| Complete Portfolio Project | 280–320 cumulative hours |
| Production Pilot | 1,800–2,200 team hours |
| Enterprise Scale-Up | Additional 1,400–1,800 team hours |

## Build and Versioning

### Procurement Copilot

Uses its existing build and release sequence.

### Packaging Value Engineering

Uses independent build identifiers:

- `PVE-0.1` Repository Foundation
- `PVE-0.2` Data Model and Demo Data
- `PVE-0.3` Cost and Material Engine
- `PVE-0.4` Technical Qualification and Risk
- `PVE-0.5` Scenario and Recommendation UI
- `PVE-0.6` Decision Package Export
- `PVE-0.7` QA and Interview Release

### Integration

Use explicit contract versions such as:

- `PVE-CONTRACT-v1.0`
- `PC-PVE-ADAPTER-v1.0`

## Mandatory Quality Rules

Every meaningful update in either repository must:

1. Update the project-local activity and build records.
2. Run project-local tests.
3. Inspect the complete diff.
4. Commit and push only to the correct repository.
5. Re-fetch the GitHub commit to confirm file placement.
6. Check CI or record why it is not applicable.
7. Store QA evidence in the same repository.

Integration changes require tests in both repositories or a documented compatibility test against a fixed contract sample.

## Immediate Sequence

1. Complete AI Procurement Copilot Build 0.9.5 CI and live validation.
2. Harden Portfolio Edition v1.0.
3. Create the separate PVE repository with governance files before any PVE code.
4. Build PVE Scope A independently.
5. Freeze `PVE-CONTRACT-v1.0`.
6. Add the PVE import adapter to Procurement Copilot.
7. Run cross-repository integration and regression tests.
