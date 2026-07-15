# Pending Work Register

Formal status values use exactly one approved classification.

| ID | Work item | Current status | Evidence / dependency | Acceptance criterion |
|---|---|---|---|---|
| REC-001 | Capture exact maintenance and v1.1 HEADs | VERIFIED COMPLETE | Direct branch refs | Exact SHAs remain recorded |
| REC-002 | Verify canonical Python/dependency environment | VERIFIED COMPLETE | GitHub Actions artifact | Python 3.11.15 and pinned requirements recorded |
| REC-003 | Run reconstructed candidate compile and full regression | VERIFIED COMPLETE | 162 passed, 1 warning | Final canonical CI remains green |
| REC-004 | Run Streamlit startup smoke | VERIFIED COMPLETE | Smoke script PASS | Preserve in final CI |
| DEF-001 | Original INR/display inconsistency | DEFECT / REGRESSION | Historical maintenance PRs | Promote only validated correction |
| DEF-002 | Reconstructed currency corrections | VERIFIED COMPLETE | Focused currency/export tests and full suite | Final review confirms no formula/schema drift |
| DEF-003 | Preserve canonical risk-TCO source in display wrapper | VERIFIED COMPLETE | Root-cause correction at `acda1738...` | USD/INR/Both tests remain green |
| UX-001 | Supplier-selector capability | VERIFIED COMPLETE | Stable code and contract tests | Existing selector remains single and mapped |
| UX-002 | Exercise every supplier option in hosted UI | NOT STARTED | Authoritative hosted URL required | Each option renders matching Supplier 360 profile |
| DEP-001 | Historical Streamlit acceptance | DOCUMENTED ONLY | Stable records | Do not represent as current proof |
| DEP-002 | Current hosted deployment health | REPORTED BUT NOT FOUND | No authoritative URL located | URL responds and app is manually accepted |
| DOC-001 | Preserve governance/portability controls in v1.0.1 | VERIFIED COMPLETE | Reconstruction from current main | Final diff retains all controls |
| GOV-002 | Confirm no net workflow change after diagnostics | NOT STARTED | Final PR diff and CI | `.github/workflows/quality-checks.yml` absent from final diff |
| ERP-001 | v1.1 ERP foundation | VERIFIED PARTIAL | Exact v1.1 HEAD recorded | Separate authorization required |
| ERP-005 | Complete ERP upload pipeline/report/UI | REPORTED BUT NOT FOUND | No authoritative implementation evidence | Remains out of Recovery R1 |
| FUT-001 | Time-aware analytics and production integrations | DEFERRED | Separate roadmap | No premature scope expansion |
| OOS-001 | Autonomous award and unapproved AI-provider expansion | OUT OF SCOPE | Governance boundary | Must not enter v1.0.1 |

## Priority Rule
PR #9 must not merge until UX-002, DEP-002 and GOV-002 are closed or the owner explicitly accepts those residual risks after final review.
