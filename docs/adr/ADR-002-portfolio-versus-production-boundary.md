# ADR-002 — Portfolio Versus Production Boundary

## Status

Accepted for current portfolio architecture, subject to governed change control.

## Context

The repository demonstrates governed procurement decision support, explainability and deterministic calculation patterns. Its hosted and repository evidence does not establish enterprise production readiness.

## Decision

Classify the project as a governed interview showcase and portfolio decision-support prototype. It is not a production system and is not currently a production candidate.

Production claims are prohibited unless supported by separately accepted evidence. Missing production capabilities include enterprise identity and authorization, production persistence, multi-user concurrency controls, approval workflow persistence, ERP write-back, production observability, high availability, disaster recovery, operating support and formal security assurance.

Do not add speculative production infrastructure solely to improve portfolio appearance.

## Decision Drivers

- Prevent unsupported capability claims.
- Preserve credibility in interviews and demonstrations.
- Avoid unnecessary implementation complexity.
- Separate proven decision-support value from future enterprise engineering.
- Keep investment proportional to current use.

## Considered Alternatives

- **Describe the application as production-ready:** rejected because evidence does not support the claim.
- **Build enterprise infrastructure immediately:** deferred until a real production case, users, controls and operating model exist.
- **Avoid classification:** rejected because ambiguity increases technical and procurement risk.

## Consequences

Documentation and demonstrations must state the portfolio boundary. Production architecture may be evaluated later through a separately authorized programme. Current CI, tests and smoke validation prove repository integrity within scope, not enterprise operational readiness.

## Risks and Controls

- **Risk:** viewers infer production readiness from a hosted application. **Control:** explicit classification and limitation statements.
- **Risk:** future features blur the boundary. **Control:** production-classification changes require governed review and evidence.
- **Risk:** excessive infrastructure reduces learning ROI. **Control:** apply the Simplicity Gate.

## Scope

Repository documentation, demonstrations, architecture decisions, release language and future infrastructure proposals.

## Non-Scope

A future production-readiness assessment or implementation programme.

## Evidence

- `PROJECT_CONTROL.md`
- `DEFINITION_OF_DONE.md`
- `SIMPLICITY_GATE.md`
- `VERIFICATION_POLICY.md`
- `PROJECT_ARCHITECTURE.md`
- `docs/07_GOVERNANCE_AND_LIMITATIONS.md`
- Merged PRs #48 and #49

## Reverification Triggers

Changes to intended users, deployment model, data classification, persistence, authentication, authorization, ERP integration, operating support, security assurance or production-readiness claims.