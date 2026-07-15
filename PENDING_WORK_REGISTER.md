# Pending Work Register

Formal status values use exactly one approved classification.

| ID | Work item | Current status | Evidence / dependency | Acceptance criterion |
|---|---|---|---|---|
| REC-001 | Recovery R1 baseline capture | VERIFIED COMPLETE | Direct branch refs | Exact SHAs preserved |
| REC-002 | Standalone main regression | VERIFIED COMPLETE | 114 passed, 1 warning; smoke PASS | Evidence retained |
| REC-003 | Reconstructed v1.0.1 regression | VERIFIED COMPLETE | 162 passed, 1 warning; smoke PASS | Evidence retained |
| REC-004 | Recovery R1 merge | VERIFIED COMPLETE | PR #9 merged as `18c009fd...` | Main contains validated maintenance |
| DEF-001 | Original INR/display inconsistency | VERIFIED COMPLETE | Corrected and merged through PR #9 | No recurrence in release evidence |
| DEF-002 | Risk-TCO source preservation | VERIFIED COMPLETE | Focused/full tests and hosted acceptance | USD/INR/Both remain correct |
| UX-001 | Supplier selector and Supplier 360 profiles | VERIFIED COMPLETE | Automated and owner-observed acceptance | Six suppliers remain mapped correctly |
| CUR-001 | Hosted USD/INR/Both modes | VERIFIED COMPLETE | Owner-observed Recovery R1 and primary-main acceptance | Labels, values, rankings and audit fields accepted |
| REL-001 | Recovery R1 maintenance merge | VERIFIED COMPLETE | Main `18c009fd...` | Validated maintenance preserved |
| REL-002 | Displayed v1.0.1 metadata correction | VERIFIED COMPLETE | Main `ae50bca0...`; scoped audit | Edition/build/docstring and regression test preserved |
| REL-003 | Audit unexpected main commit | VERIFIED COMPLETE | Five-file commit audit | No procurement logic, formula, schema, v1.1 or ERP change |
| REL-004 | Reconstruct release closure from current main | VERIFIED COMPLETE | `release/v1.0.1-closure-reconciled` | Eight Markdown documents rebuilt |
| REL-005 | Replace PR #10 head with reconciled branch | NOT STARTED | REL-004 | PR based cleanly on current main |
| REL-006 | Verify final eight-file PR boundary | NOT STARTED | REL-005 | Only approved Markdown paths remain |
| REL-007 | Run final reconciled Quality Checks | NOT STARTED | REL-005 | Install, compile, pytest and smoke PASS with exact totals |
| REL-008 | Merge release-closure PR | NOT STARTED | Owner approval and REL-006/007 | Documentation-only PR merged to main |
| REL-009 | Create annotated tag `v1.0.1` | NOT STARTED | REL-008 and final main SHA | Tag points to final approved main SHA |
| REL-010 | Create GitHub release `Portfolio Edition v1.0.1` | NOT STARTED | REL-009 | Approved notes published without changing v1.0.0 |
| ERP-001 | v1.1 ERP foundation | VERIFIED PARTIAL | Separate branch and authorization | Remains outside v1.0.1 closure |
| FUT-001 | Time-aware analytics and production integrations | DEFERRED | Separate roadmap | No premature scope expansion |
| OOS-001 | Autonomous award and unapproved AI-provider expansion | OUT OF SCOPE | Governance boundary | Must not enter v1.0.1 |

## Priority Rule
Complete REL-005 through REL-010 in sequence. Do not merge, tag, publish a release or begin Version 1.1 implementation before final reconciled CI and renewed owner approval.
