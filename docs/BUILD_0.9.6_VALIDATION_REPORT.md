# Build 0.9.6 Validation Report

## Build

Build 0.9.6 — Independent Validation and Real-World Stress Testing

## Status

**Implementation complete; CI, live deployment, Gemini, Perplexity and human review pending.**

Build 0.9.6 cannot be marked fully complete until all release gates are evidenced.

## Safety controls implemented

- Data-confidence engine
- Recommendation eligibility gate
- Business-rule validator
- Validation-assurance orchestration
- Final-award narrative withholding
- Mixed-currency and mixed-unit blockers
- Positive price and positive annual-volume gates
- Percentage range and decimal-format warnings
- Capacity sufficiency and allocation feasibility checks
- Transparent demo/upload source labels
- Defaulted, inferred and missing-critical data visibility

## Audit assets

- Formula register
- Assumption register
- Decision-rule register
- Input-output traceability
- Known model limitations
- Expected result matrix
- Validation defect register
- Release-readiness scorecard
- Model-risk statement

## Test assets

- Data-confidence tests
- Recommendation-eligibility tests
- Business-rule tests
- Logic-audit invariants
- Adversarial input tests
- Synthetic real-world file tests
- Fourteen packaging, raw-material and edge-case validation datasets

## Defects identified internally

| ID | Severity | Summary | Remediation |
|---|---|---|---|
| VAL-001 | Critical | Final award language lacked central eligibility gate | Gate and safe narrative withholding added |
| VAL-002 | Major | Supplier 360 defaults could create false confidence | Defaults now reduce and explain data confidence |
| VAL-003 | Critical | Allocation needed independent capacity feasibility validation | 100% and capacity checks added |
| VAL-004 | Critical | Mixed currencies/UOMs needed a final comparison blocker | Consistency blockers added |
| VAL-005 | Major | Decimal-versus-whole percentage ambiguity | Explicit warning and test case added |

## Provisional results

- Formula documentation: Complete internally
- Safety-control code: Implemented
- Adversarial dataset library: Implemented
- Regression tests: Added
- External-file synthetic test library: Implemented
- Independent AI review: Pending
- Human review: Pending
- GitHub Actions: Pending latest run
- Live Streamlit validation: Pending
- Provisional release-readiness score: 9.1/10

## Completion gate

Do not approve Portfolio Edition v1.0 until:

1. Latest CI is green.
2. Packaging and Raw Material live workflows are manually validated.
3. Gemini report is completed and dispositioned.
4. Perplexity methodology review is completed and dispositioned.
5. Human review is completed or formally waived.
6. All Critical defects are closed and retested.
7. No unmitigated Major defects remain.
8. Final scorecard remains at least 9.0/10.
