# Pending Work Register

Formal status values use exactly one approved classification.

| ID | Work item | Current status | Evidence / dependency | Acceptance criterion |
|---|---|---|---|---|
| REC-001 | Capture exact maintenance and v1.1 HEADs | VERIFIED COMPLETE | Direct branch refs | Exact SHAs remain recorded |
| REC-002 | Verify exact canonical main environment and regression | VERIFIED COMPLETE | Run 377; artifact digest recorded | 114 passed, 1 warning; smoke PASS |
| REC-003 | Run reconstructed candidate compile and regression | VERIFIED COMPLETE | 162 passed, 1 warning | Final canonical CI remains green |
| REC-004 | Run Streamlit startup smoke | VERIFIED COMPLETE | Main and candidate smoke PASS | Preserve canonical smoke gate |
| DEF-001 | Original INR/display inconsistency | DEFECT / REGRESSION | Historical maintenance PRs | Promote only validated correction |
| DEF-002 | Reconstructed currency corrections | VERIFIED COMPLETE | Focused currency/export tests and full suite | No formula/schema drift |
| DEF-003 | Preserve canonical risk-TCO source | VERIFIED COMPLETE | Root-cause correction at `acda1738...` | USD/INR/Both tests remain green |
| UX-001 | Supplier-selector capability | VERIFIED COMPLETE | Stable code and contract tests | Existing selector remains single and mapped |
| UX-002 | Exercise all packaging suppliers in hosted UI | NOT STARTED | Authoritative hosted URL required | Three packaging suppliers map correctly |
| UX-003 | Exercise all raw-material suppliers in hosted UI | NOT STARTED | Authoritative hosted URL required | Three raw-material suppliers map correctly |
| CUR-001 | Validate hosted USD/INR/Both modes | NOT STARTED | Authoritative hosted URL required | Labels, values, rankings and audit fields accepted |
| DEP-001 | Historical Streamlit acceptance | DOCUMENTED ONLY | Stable records | Do not represent as current proof |
| DEP-002 | Authoritative hosted URL and current health | REPORTED BUT NOT FOUND | Repository search returned none | URL responds and app is manually accepted |
| DOC-001 | Preserve governance/portability controls | VERIFIED COMPLETE | Reconstruction from current main | Final diff retains controls |
| GOV-002 | Confirm no net workflow change | VERIFIED COMPLETE | Final PR filename review | Workflow path absent from PR diff |
| ERP-001 | v1.1 ERP foundation | VERIFIED PARTIAL | Exact v1.1 HEAD recorded | Separate authorization required |
| ERP-005 | Complete ERP upload pipeline/report/UI | REPORTED BUT NOT FOUND | No authoritative evidence | Remains out of Recovery R1 |
| FUT-001 | Time-aware analytics and production integrations | DEFERRED | Separate roadmap | No premature scope expansion |
| OOS-001 | Autonomous award and unapproved AI-provider expansion | OUT OF SCOPE | Governance boundary | Must not enter v1.0.1 |

## Priority Rule
PR #9 must not merge until UX-002, UX-003, CUR-001 and DEP-002 are closed, or the owner explicitly accepts those residual hosted-validation risks after final review.
