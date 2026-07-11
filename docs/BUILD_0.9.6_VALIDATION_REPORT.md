# Build 0.9.6 Validation Report

## Build

Build 0.9.6 — Independent Validation and Real-World Stress Testing

## Status

**Implementation and CI validation complete; live deployment, Gemini, Perplexity and human review pending.**

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

| ID | Severity | Summary | Remediation | Retest status |
|---|---|---|---|---|
| VAL-001 | Critical | Final award language lacked central eligibility gate | Gate and safe narrative withholding added | Passed CI |
| VAL-002 | Major | Supplier 360 defaults could create false confidence | Defaults now reduce and explain data confidence | Passed CI |
| VAL-003 | Critical | Allocation needed independent capacity feasibility validation | 100% and capacity checks added | Passed CI |
| VAL-004 | Critical | Mixed currencies/UOMs needed a final comparison blocker | Consistency blockers added | Passed CI |
| VAL-005 | Major | Decimal-versus-whole percentage ambiguity | Explicit warning and test case added | Passed CI |

## Current results

- Formula documentation: Complete internally
- Safety-control code: Implemented
- Adversarial dataset library: Implemented
- Regression tests: Added and passing
- External-file synthetic test library: Implemented and passing in CI
- GitHub Quality Checks #150–#208: Confirmed green by project owner
- Internal Critical and Major defects: Fixed and CI retested
- Independent AI review: Pending
- Human review: Pending
- Live Streamlit validation: Pending
- Provisional release-readiness score: 9.2/10

## Completion gate

Do not approve Portfolio Edition v1.0 until:

1. Packaging and Raw Material live workflows are manually validated.
2. Gemini report is completed and dispositioned.
3. Perplexity methodology review is completed and dispositioned.
4. Human review is completed or formally waived.
5. External review confirms no open Critical defect.
6. No unmitigated Major defect remains.
7. Final scorecard remains at least 9.0/10.
