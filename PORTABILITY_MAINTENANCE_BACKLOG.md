# Portability Maintenance Backlog

## Status

All items in this document are **optional future hardening**. They are not blockers for Portfolio Edition v1.0.0, do not indicate a current defect, and should be implemented only when the additional governance value justifies the effort.

## 1. Manual Quality Checks Trigger

**Objective:** Add `workflow_dispatch` to the existing Quality Checks workflow so an authorized maintainer can run post-merge verification manually when a formal CI record is required.

**Scope:**

- Add a manual trigger to the existing workflow.
- Preserve the current push and pull-request triggers.
- Run the same Python compilation, pytest regression suite, and Streamlit smoke test.
- Do not change application behaviour or calculation logic.

**Value:** Provides explicit post-merge or audit evidence without requiring a repository-content change solely to trigger CI.

**Priority:** Optional future hardening.

## 2. Exact Rule-to-Test Traceability

**Objective:** Extend formula and governance traceability from test categories to exact test filenames and test-function names.

**Scope:**

- Map every protected formula, threshold, default, eligibility rule, normalization rule, and output-control rule to its authoritative test file and test function.
- Identify rules that are currently covered only indirectly.
- Record any future boundary-test requirement without changing existing formulas or tests in the documentation task itself.

**Value:** Reduces regression-analysis effort and makes future rule changes easier to review across humans and AI assistants.

**Priority:** Optional future hardening.

## 3. Documentation Ownership and Update Governance

**Objective:** Assign clear ownership for documentation and protected decision-rule records using `CODEOWNERS` or an equivalent documented ownership table.

**Scope:**

- Define ownership for architecture, formulas, data definitions, CI/workflows, release documentation, and contribution standards.
- Require relevant documentation updates when formulas, schemas, aliases, defaults, thresholds, workflows, or module responsibilities change.
- Keep human approval mandatory for protected procurement decision rules.

**Value:** Reduces documentation drift and clarifies who must review future changes.

**Priority:** Optional future hardening.

## 4. Fresh-Agent Portability Validation Exercise

**Objective:** Test whether a new AI assistant or human developer can understand and validate the repository without prior chat history.

**Exercise coverage:**

- Identify the system architecture and major workflow owners.
- Locate authoritative supplier-scoring, TCO, risk, and eligibility formulas.
- Identify canonical RFQ fields, accepted aliases, defaults, and missing-data behaviour.
- Explain recommendation eligibility and final-award-language controls.
- State the commands required for Python compilation, pytest regression testing, and the Streamlit smoke test.

**Acceptance expectation:** The fresh agent should answer from repository documentation and authoritative source files, clearly distinguish documentation from executable authority, avoid inventing unsupported rules, and preserve mandatory human approval.

**Value:** Provides a practical portability test rather than relying only on document completeness.

**Priority:** Optional future hardening.

## Governance Boundary

Completing any backlog item requires a focused task, explicit review, and validation appropriate to the files changed. These items must not be used as justification for unapproved changes to application logic, formulas, dependencies, tests, workflows, or runtime behaviour.