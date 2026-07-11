# Master Build Architecture

## Project

AI Procurement Copilot with Packaging Value Engineering & Decision Intelligence

## Canonical Source of Truth

GitHub repository: `pratikoperations/AI-Procurement-Copilot`

All code, data schemas, business rules, decisions, build plans, QA evidence, activity logs, versions, and recovery instructions must be stored in this repository. Chat history is supporting context only and must never be required to resume the project.

## Product Architecture

```text
AI Procurement Copilot
├── Executive Dashboard
├── Intelligent RFQ Engine
├── Category Engine Router
│   ├── Packaging Procurement
│   │   └── Packaging Value Engineering & Decision Intelligence
│   └── Raw Material Procurement
├── Procurement Intelligence
│   ├── Should-Cost
│   ├── TCO
│   ├── Supplier Comparison
│   ├── Allocation
│   ├── Negotiation
│   └── Scenario Analysis
├── Supplier Intelligence
│   ├── Supplier 360
│   ├── Performance
│   ├── Financial Indicators
│   ├── ESG
│   ├── Innovation
│   └── SRM
├── Savings Realization
├── Decision Evidence Ledger
├── Explainability and Executive Outputs
└── Validation, QA, CI, Recovery, and Governance
```

## Packaging Value Engineering Scope

The Packaging Value Engineering module is a specialist vertical inside the Copilot. It must not duplicate supplier comparison, negotiation, allocation, or savings tracking already owned by the horizontal Procurement Copilot.

### Core Decision Flow

```text
Spend / RFQ Opportunity
→ Packaging Baseline
→ Alternative Design Comparison
→ Should-Cost and Material Impact
→ Technical Qualification Gate
→ Risk-Adjusted Savings
→ Supplier and TCO Evaluation
→ Negotiation and Allocation
→ Trial / Validation
→ Implementation
→ Verified Savings
```

## Scope Options

### Scope A — Lean Interview Module

Target effort: 80–110 hours.

Includes:

- One packaging category
- Packaging baseline and alternatives
- Should-cost and material calculations
- Technical qualification and risk rules
- Risk-adjusted savings
- Linkage to supplier comparison, TCO, negotiation, and executive recommendation
- Basic explainability
- Core testing and interview walkthrough

Exit condition: reliable five-minute interview demonstration with traceable calculations and clear limitations.

### Scope B — Robust Interview Version

Target cumulative effort: 150–200 hours.

Adds:

- Scenario and sensitivity analysis
- Savings realization
- Decision Evidence Ledger
- Stronger data-quality controls
- Downloadable executive decision record
- Expanded QA and edge-case testing
- Improved UI and portfolio documentation

Exit condition: portfolio-grade application demonstrating business execution, governance, and auditable decision support.

### Scope C — Complete Integrated Portfolio Version

Target cumulative effort: approximately 280–320 hours.

Adds:

- Trial and validation workflow
- Historical packaging knowledge retrieval
- Opportunity prioritization
- Advanced confidence scoring
- Additional packaging category
- Extended reporting and recovery assets
- Full regression suite and release hardening

Exit condition: comprehensive, modular portfolio platform with a credible enterprise roadmap.

### Scope D — Production Pilot

Target effort: 1,800–2,200 cross-functional team hours over 3–5 months.

Includes:

- Real data discovery and cleansing
- Production database and APIs
- Authentication and role-based access
- Approval workflows and audit logs
- One category or site pilot
- Controlled AI capabilities
- ERP, PLM, QMS, or supplier-data integrations as available
- User acceptance testing and measurable value validation

### Scope E — Enterprise Scale-Up

Target additional effort: 1,400–1,800 team hours over 5–7 months.

Includes:

- Multi-category models
- Additional sites and business units
- Enterprise integrations
- Security hardening
- Support and release operations
- Change management
- Adoption and value dashboards

## Build Numbering Standard

- Existing platform builds remain `Build 0.x.x` until Portfolio Edition v1.0 release.
- Packaging Value Engineering work uses sub-build identifiers under the active milestone, for example:
  - `Build 1.0-PVE-01`
  - `Build 1.0-PVE-02`
- Major milestone releases use semantic versions:
  - `v1.0` Portfolio Edition release
  - `v1.1` Packaging Value Engineering interview module
  - `v1.2` Robust integrated decision version
  - `v2.0` Production-pilot architecture
- A version is never advanced solely for documentation wording; it advances when the defined exit criteria are met.

## Mandatory Repository Records

Every meaningful build update must update the relevant records:

- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `BUILD_HISTORY.md`
- `DECISION_LOG.md`
- `ACTIVITY_LOG.md`
- `VERSION_MANIFEST.md`
- `RECOVERY_MANIFEST.md`
- Build-specific QA report in `docs/`

## Build Update Workflow

1. Read `PROJECT_STATUS.md`, `RECOVERY_MANIFEST.md`, latest `BUILD_HISTORY.md`, and latest QA report.
2. Confirm current branch, build number, scope, dependencies, and acceptance criteria.
3. Implement one coherent build unit only.
4. Run relevant tests and quality checks.
5. Update activity, build, decision, changelog, version, status, and recovery records.
6. Inspect the full diff for unrelated changes.
7. Commit with the build identifier and a concise description.
8. Push the branch.
9. Verify the commit and repository files from GitHub.
10. Check CI or record why CI is not applicable.
11. Do not mark the build complete until QA evidence is stored in GitHub.

## Quality Gates

A build cannot be declared complete unless all applicable gates pass:

- Scope gate: only approved build scope changed
- Calculation gate: deterministic formulas validated
- Data gate: required fields, units, defaults, and assumptions checked
- Business-rule gate: triggered rules and outcomes tested
- Integration gate: upstream and downstream linkages tested
- Regression gate: existing functions remain operational
- Explainability gate: recommendation can be traced to evidence
- Documentation gate: all mandatory repository records updated
- Recovery gate: a new chat or developer can resume using repository content alone
- CI gate: automated checks pass or the exception is explicitly recorded

## Architecture Principles

- Deterministic calculations and business rules are the source of truth.
- AI is used for extraction, synthesis, explanation, and drafting—not autonomous award or technical approval.
- Technical qualification precedes commercial ranking.
- Recommendations may be Recommended, Conditionally Recommended, Not Recommended, or Insufficient Data.
- Every recommendation must expose assumptions, data gaps, confidence, and required validation.
- Savings are not considered delivered until implementation and actual-volume evidence exists.
- Category-specific technical logic must remain separate from common procurement logic.
- Shared entities include supplier, material, specification, quote, plant, SKU, trial, risk, project, decision, and savings record.

## Immediate Priority

Do not add uncontrolled feature breadth before Build 0.9.5 CI and live validation are complete.

After Portfolio Edition v1.0 release hardening, begin Scope A as the next controlled milestone.
