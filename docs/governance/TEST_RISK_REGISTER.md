# Business-Risk Test Register

## Purpose

This register evaluates validation by procurement and architecture risk rather than by test count. It maps material risks to authoritative components, existing preventive controls, direct test evidence, Gate 3B validation needs, blocking behaviour and closure evidence.

The register is a governance index. It does not replace executable tests, source code, CI evidence, business rules, ADRs or governed review records.

## Governing principles

- Test count is not a quality objective.
- Every material test should map to a business or architecture risk.
- Higher-risk controls require stronger and more direct evidence.
- Existing tests are reused when they directly cover the relevant boundary or failure mode.
- Duplicate tests are rejected unless they cover a distinct boundary, consumer or failure mode.
- Documentation-only changes do not require invented focused code tests; full repository CI remains required where configured.
- Automated smoke proves startup and basic runtime integrity, not browser, mobile, accessibility or production certification.
- A risk is marked **Covered** only where direct evidence exists for the stated boundary. Route, UI, export or hosted coverage is not inferred from isolated engine tests.

## Status definitions

### Coverage state

- **Covered** — direct evidence exercises the stated control and failure mode.
- **Partially Covered** — direct evidence covers part of the risk, but a material consumer, route or failure boundary remains.
- **Gap** — no direct evidence currently covers the material risk boundary.
- **Not Applicable** — the risk does not apply to the authorized scope.
- **Deferred with Rationale** — coverage is intentionally deferred with explicit reasoning and acceptance conditions.

### Priority

- **Blocker** — must be closed before Gate 3B merge.
- **High** — requires direct evidence before Gate 3B closure unless formally accepted with rationale.
- **Medium** — should be addressed when the affected boundary changes.
- **Low** — monitor; no current Gate 3B closure dependency.

## Evidence hierarchy

1. Immutable Git objects and current refs.
2. CI evidence tied to exact SHAs.
3. Executable contracts, code and tests.
4. This register and accepted ADRs as governance records.

Primary sources include `PROJECT_CONTROL.md`, `DEFINITION_OF_DONE.md`, `SIMPLICITY_GATE.md`, `VERIFICATION_POLICY.md`, `PROJECT_ARCHITECTURE.md`, `BUSINESS_RULES.md`, `FORMULA_TRACEABILITY_REGISTER.md`, `docs/adr/README.md`, ADR-001 through ADR-008, `modules/allocation_contract.py`, `modules/multi_supplier_allocation.py`, `modules/multi_supplier_allocation_adapter.py`, relevant tests, merged PRs #45–#50 and accepted CI runs 845, 848, 850 and 852.

## Risk register

### TR-001 — UI or presentation becomes a second calculation authority
- **Procurement or business impact:** Conflicting recommendations, costs, rankings or allocations undermine decision credibility.
- **Failure mode:** UI, sidebar, presenter or export derives business values independently.
- **Authoritative component:** Category engines, governed contracts and `modules/multi_supplier_allocation.py`.
- **Existing preventive control:** ADR-001, ADR-005, ADR-008; `SIMPLICITY_GATE.md`.
- **Existing test evidence:** Presenter and public-presentation tests cover selected read-only behaviours, but no Gate 3B end-to-end authority test exists.
- **Coverage state:** Gap.
- **Required Gate 3B validation:** Route-level test proving all visible allocation values originate from one engine result and no presenter recalculates them.
- **Severity / Likelihood / Detectability:** Critical / Medium / Medium.
- **Overall priority:** Blocker.
- **Blocking behaviour:** Gate 3B merge blocked if any UI-side canonical calculation or duplicate authority remains.
- **Evidence required for closure:** Focused route/UI tests, result identity reconciliation and governed review.
- **Reverification triggers:** UI route, presenter, dashboard, export or engine ownership changes.
- **Owner or accountable role:** Application architect and procurement product owner.

### TR-002 — Legacy allocation appears beside the Gate 2 authoritative result
- **Procurement or business impact:** Users may choose between contradictory recommendations without a governed basis.
- **Failure mode:** Legacy and Gate 2 allocations are both visible or treated as equivalent.
- **Authoritative component:** `AIPC-MULTI-ALLOC-ENGINE-1.0`.
- **Existing preventive control:** ADR-001 and ADR-006.
- **Existing test evidence:** Engine tests establish the new authority; no application-route test proves legacy output is isolated.
- **Coverage state:** Gap.
- **Required Gate 3B validation:** Verify only the Gate 2 result is presented as authoritative and legacy output is absent or explicitly non-authoritative.
- **Severity / Likelihood / Detectability:** Critical / Medium / Easy.
- **Overall priority:** Blocker.
- **Blocking behaviour:** Merge blocked if competing visible allocation recommendations remain.
- **Evidence required for closure:** Application-route tests and manual UI inspection.
- **Reverification triggers:** Legacy compatibility, route or allocation display changes.
- **Owner or accountable role:** Application architect.

### TR-003 — Ineligible supplier enters scoring, ranking or allocation
- **Procurement or business impact:** Mandatory qualification failure is overridden by commercial attractiveness.
- **Failure mode:** Ineligible supplier receives rank, positive share or award role.
- **Authoritative component:** Eligibility contracts and allocation engine.
- **Existing preventive control:** ADR-004 and allocation contract validation.
- **Existing test evidence:** `tests/test_multi_supplier_allocation_engine.py`, `tests/test_recommendation_eligibility.py`, `tests/test_multi_supplier_allocation_adapter.py`.
- **Coverage state:** Covered.
- **Required Gate 3B validation:** Route-level assertion that exclusions remain explicit and receive no allocation.
- **Severity / Likelihood / Detectability:** Critical / Low / Easy.
- **Overall priority:** Blocker.
- **Blocking behaviour:** Any ineligible supplier with positive allocation blocks merge.
- **Evidence required for closure:** Existing engine evidence plus Gate 3B route regression.
- **Reverification triggers:** Eligibility, ranking, adapter or route changes.
- **Owner or accountable role:** Procurement rules owner.

### TR-004 — Missing technical eligibility silently defaults to true
- **Procurement or business impact:** Supplier may be recommended without verified qualification evidence.
- **Failure mode:** Missing or ambiguous eligibility becomes eligible.
- **Authoritative component:** Allocation adapter and supplier input contract.
- **Existing preventive control:** ADR-004 and fail-closed adapter statuses.
- **Existing test evidence:** `tests/test_multi_supplier_allocation_adapter.py` and `tests/test_multi_supplier_allocation_engine.py` directly reject missing or ambiguous eligibility.
- **Coverage state:** Covered.
- **Required Gate 3B validation:** Application route must surface blocked status and must not substitute a default.
- **Severity / Likelihood / Detectability:** Critical / Low / Easy.
- **Overall priority:** Blocker.
- **Blocking behaviour:** Missing eligibility must block recommendation construction.
- **Evidence required for closure:** Route failure-state test and visible blocked message.
- **Reverification triggers:** Column mapping, defaults, adapter or UI fallback changes.
- **Owner or accountable role:** Adapter owner.

### TR-005 — Missing supplier capacity is inferred from demand or annual volume
- **Procurement or business impact:** Allocation may exceed real supplier capability and create service risk.
- **Failure mode:** Demand or annual volume is reused as supplier capacity.
- **Authoritative component:** Adapter capacity evidence and feasibility engine.
- **Existing preventive control:** ADR-004 and explicit capacity requirement.
- **Existing test evidence:** `tests/test_multi_supplier_allocation_adapter.py` blocks missing/invalid capacity; feasibility and engine tests enforce capacity ceilings.
- **Coverage state:** Covered.
- **Required Gate 3B validation:** Confirm every route supplies explicit capacity evidence and blocked state is visible.
- **Severity / Likelihood / Detectability:** Critical / Medium / Easy.
- **Overall priority:** Blocker.
- **Blocking behaviour:** Missing capacity blocks allocation readiness.
- **Evidence required for closure:** Cross-category route fixtures with explicit capacity provenance.
- **Reverification triggers:** Category normalization, capacity aliases or fallback changes.
- **Owner or accountable role:** Category adapter owner.

### TR-006 — Display currency changes canonical ranking or allocation
- **Procurement or business impact:** Presentation choice changes sourcing outcome.
- **Failure mode:** Display currency alters canonical cost, rank or share.
- **Authoritative component:** Governed normalized currency and allocation inputs.
- **Existing preventive control:** ADR-005.
- **Existing test evidence:** `tests/test_currency_display.py`, `tests/test_currency_unit_integrity.py` and category currency tests cover display integrity; Gate 3B allocation-route invariance is not yet direct.
- **Coverage state:** Partially Covered.
- **Required Gate 3B validation:** Parameterized route test proving identical supplier order and allocation across display currencies.
- **Severity / Likelihood / Detectability:** Critical / Medium / Medium.
- **Overall priority:** Blocker.
- **Blocking behaviour:** Any display-driven rank or allocation change blocks merge.
- **Evidence required for closure:** Canonical-result identity comparison across display selections.
- **Reverification triggers:** Currency controls, FX conversion, ranking or export changes.
- **Owner or accountable role:** Currency governance owner.

### TR-007 — FX assumptions lack provenance or deterministic reuse
- **Procurement or business impact:** Supplier comparison cannot be reproduced or audited.
- **Failure mode:** Different consumers use different rates, dates or origins.
- **Authoritative component:** Currency and assumption governance modules.
- **Existing preventive control:** ADR-005, ADR-007 and assumption provenance controls.
- **Existing test evidence:** Currency, precedence and provenance tests provide component coverage; cross-consumer Gate 3B reuse remains unverified.
- **Coverage state:** Partially Covered.
- **Required Gate 3B validation:** Assert one FX assumption identity and effective value are reused by route, UI and exports.
- **Severity / Likelihood / Detectability:** High / Medium / Medium.
- **Overall priority:** High.
- **Blocking behaviour:** Missing FX provenance blocks comparison readiness where FX is required.
- **Evidence required for closure:** Provenance fields, deterministic repeated-run test and export reconciliation.
- **Reverification triggers:** FX source, effective date, rounding or consumer changes.
- **Owner or accountable role:** Assumption governance owner.

### TR-008 — Gate 3A adapter executes or duplicates allocation
- **Procurement or business impact:** Two allocation authorities can diverge.
- **Failure mode:** Adapter produces shares, supplier selection or optimization.
- **Authoritative component:** Adapter contract construction versus Gate 2 engine execution.
- **Existing preventive control:** ADR-001 and ADR-006.
- **Existing test evidence:** `tests/test_multi_supplier_allocation_adapter.py` validates construction, versions and human review without allocation execution.
- **Coverage state:** Covered.
- **Required Gate 3B validation:** Spy or contract test showing the route invokes the shared engine after adapter readiness and uses its result unchanged.
- **Severity / Likelihood / Detectability:** Critical / Low / Easy.
- **Overall priority:** Blocker.
- **Blocking behaviour:** Any adapter-generated allocation blocks merge.
- **Evidence required for closure:** Route invocation and result-identity test.
- **Reverification triggers:** Adapter responsibilities or orchestration changes.
- **Owner or accountable role:** Allocation architecture owner.

### TR-009 — Exactly-K allocation is violated
- **Procurement or business impact:** Award strategy and continuity intent are not met.
- **Failure mode:** Positive allocations are assigned to more or fewer than K suppliers.
- **Authoritative component:** `modules/multi_supplier_allocation.py`.
- **Existing preventive control:** Engine contract and ADR-006.
- **Existing test evidence:** `tests/test_multi_supplier_allocation_engine.py` directly tests K=1, K=2, K=3, positive-share identity and 100% reconciliation.
- **Coverage state:** Covered.
- **Required Gate 3B validation:** Route-level assertion preserving selected IDs and exactly-K semantics.
- **Severity / Likelihood / Detectability:** Critical / Low / Easy.
- **Overall priority:** Blocker.
- **Blocking behaviour:** Any non-exact K recommendation blocks merge.
- **Evidence required for closure:** Existing engine tests plus route result reconciliation.
- **Reverification triggers:** K controls, engine version or route transformation changes.
- **Owner or accountable role:** Allocation engine owner.

### TR-010 — Tie-breaking becomes nondeterministic
- **Procurement or business impact:** Equivalent inputs produce inconsistent supplier choices.
- **Failure mode:** Input order, runtime or presentation order changes selection.
- **Authoritative component:** Allocation engine deterministic ordering.
- **Existing preventive control:** ADR-006.
- **Existing test evidence:** `tests/test_multi_supplier_allocation_engine.py` tests lexical tie-breaking, reversed inputs and repeated execution.
- **Coverage state:** Covered.
- **Required Gate 3B validation:** Repeat application-route execution with shuffled rows and compare serialized result.
- **Severity / Likelihood / Detectability:** High / Low / Medium.
- **Overall priority:** High.
- **Blocking behaviour:** Nondeterministic selected suppliers or shares block merge.
- **Evidence required for closure:** Repeated and shuffled-input route tests.
- **Reverification triggers:** Sorting, ranking, engine or serialization changes.
- **Owner or accountable role:** Allocation engine owner.

### TR-011 — Infeasible capacity or constraints produce a misleading recommendation
- **Procurement or business impact:** Recommended award cannot satisfy demand or governed constraints.
- **Failure mode:** Infeasible or indeterminate state is presented as recommended allocation.
- **Authoritative component:** Feasibility and allocation status contracts.
- **Existing preventive control:** Explicit feasibility and failure statuses.
- **Existing test evidence:** `tests/test_multi_supplier_allocation_feasibility.py` and `tests/test_multi_supplier_allocation_engine.py` test insufficient capacity, indeterminate feasibility and no exact allocation.
- **Coverage state:** Covered.
- **Required Gate 3B validation:** Route must preserve blocked status, reasons and absence of recommendation.
- **Severity / Likelihood / Detectability:** Critical / Medium / Easy.
- **Overall priority:** Blocker.
- **Blocking behaviour:** No recommendation may be displayed when feasibility is unconfirmed.
- **Evidence required for closure:** Application failure-state tests and manual visibility check.
- **Reverification triggers:** Constraint, capacity, status or presentation changes.
- **Owner or accountable role:** Feasibility owner.

### TR-012 — Partial evidence captured before adapter failure is shown as complete
- **Procurement or business impact:** Reviewers may trust an incomplete evidence package.
- **Failure mode:** Evidence collected before failure is labelled complete or ready.
- **Authoritative component:** Adapter status and evidence presentation.
- **Existing preventive control:** Gate 3B residual label requirement: “Partial evidence captured before adapter failure”.
- **Existing test evidence:** Adapter blocking tests exist; no direct UI evidence-completeness test exists.
- **Coverage state:** Gap.
- **Required Gate 3B validation:** Force late adapter failure and verify partial-evidence label, blocked status and no complete-evidence claim.
- **Severity / Likelihood / Detectability:** Critical / Medium / Medium.
- **Overall priority:** Blocker.
- **Blocking behaviour:** Merge blocked if partial evidence can be shown as complete.
- **Evidence required for closure:** Focused presenter/UI test and manual screenshot evidence.
- **Reverification triggers:** Adapter evidence accumulation or failure presentation changes.
- **Owner or accountable role:** Evidence assurance owner.

### TR-013 — Evidence origin is missing, contradictory or silently relabelled
- **Procurement or business impact:** Assumptions and supplier evidence lose auditability.
- **Failure mode:** Origin is absent, contradictory or converted to a more authoritative source.
- **Authoritative component:** Adapter evidence-origin governance.
- **Existing preventive control:** ADR-007 and source-type/origin rules.
- **Existing test evidence:** `tests/test_multi_supplier_allocation_adapter.py` directly tests fixed origins, contradictory origins, category-adapter explicit origin and deterministic reasons.
- **Coverage state:** Covered.
- **Required Gate 3B validation:** Preserve origin fields through route and visible evidence views.
- **Severity / Likelihood / Detectability:** Critical / Medium / Easy.
- **Overall priority:** Blocker.
- **Blocking behaviour:** Missing required or contradictory origin blocks readiness.
- **Evidence required for closure:** Route serialization and UI evidence-origin assertions.
- **Reverification triggers:** Source types, aliases, provenance schema or UI changes.
- **Owner or accountable role:** Evidence governance owner.

### TR-014 — UI overrides authoritative parameter precedence
- **Procurement or business impact:** User controls silently replace governed evidence or defaults.
- **Failure mode:** Presentation layer applies a different last-value-wins precedence.
- **Authoritative component:** Parameter precedence contracts and category authorities.
- **Existing preventive control:** ADR-007.
- **Existing test evidence:** Component precedence tests exist, but no Gate 3B UI-to-route precedence test exists.
- **Coverage state:** Gap.
- **Required Gate 3B validation:** Parameterized tests across supplied, workbook, category-default and controlled-synthetic values; verify origin and selected value.
- **Severity / Likelihood / Detectability:** Critical / Medium / Difficult.
- **Overall priority:** Blocker.
- **Blocking behaviour:** Any silent UI precedence override blocks merge.
- **Evidence required for closure:** Route input trace, origin assertions and conflict-failure tests.
- **Reverification triggers:** Sidebar controls, route inputs, workbook ingestion or defaults.
- **Owner or accountable role:** Input governance owner.

### TR-015 — Trace metadata or SourceMate recalculates business values
- **Procurement or business impact:** Explanation layer may contradict authoritative output.
- **Failure mode:** Presenter evaluates formulas or derives substitute cost, score or allocation.
- **Authoritative component:** Executable engines and immutable trace evidence.
- **Existing preventive control:** ADR-008.
- **Existing test evidence:** Calculation explorer and trace reconciliation tests cover read-only patterns; SourceMate and Gate 3B integration are not fully implemented.
- **Coverage state:** Partially Covered.
- **Required Gate 3B validation:** Presenter tests proving values are read from result/trace contracts and no calculation function is invoked.
- **Severity / Likelihood / Detectability:** Critical / Medium / Difficult.
- **Overall priority:** Blocker.
- **Blocking behaviour:** Substitute presenter calculation blocks merge.
- **Evidence required for closure:** Static review, focused tests and result/trace identity checks.
- **Reverification triggers:** SourceMate, explorer, metadata or presenter changes.
- **Owner or accountable role:** Explainability owner.

### TR-016 — Narrative conflicts with executable output
- **Procurement or business impact:** User may follow an incorrect explanation instead of the governed result.
- **Failure mode:** Narrative changes supplier status, rank, share or recommendation meaning.
- **Authoritative component:** Executable result contract.
- **Existing preventive control:** ADR-003 and ADR-008.
- **Existing test evidence:** Public-presentation and governed-recommendation tests cover advisory wording; no comprehensive Gate 3B narrative/result reconciliation exists.
- **Coverage state:** Partially Covered.
- **Required Gate 3B validation:** Deliberate mismatch fixture must disclose conflict and preserve executable result.
- **Severity / Likelihood / Detectability:** High / Medium / Medium.
- **Overall priority:** High.
- **Blocking behaviour:** Narrative cannot override or silently contradict executable status.
- **Evidence required for closure:** Presenter tests and governed review of visible language.
- **Reverification triggers:** Narrative templates, AI generation or result schema changes.
- **Owner or accountable role:** Explainability and procurement governance owners.

### TR-017 — Human procurement approval is omitted or obscured
- **Procurement or business impact:** Recommendation may be interpreted as authorization.
- **Failure mode:** Human-review requirement is absent from result or visible output.
- **Authoritative component:** Allocation result contract and presentation.
- **Existing preventive control:** ADR-003 and contract warnings.
- **Existing test evidence:** Adapter and engine tests assert `human_review_required`; governed recommendation tests cover approval language.
- **Coverage state:** Covered.
- **Required Gate 3B validation:** Verify visible approval notice in successful, warning and blocked states.
- **Severity / Likelihood / Detectability:** Critical / Medium / Easy.
- **Overall priority:** Blocker.
- **Blocking behaviour:** Missing visible human-approval boundary blocks merge.
- **Evidence required for closure:** UI contract test and manual browser validation.
- **Reverification triggers:** Result status, UI copy, exports or workflow changes.
- **Owner or accountable role:** Procurement product owner.

### TR-018 — Output is presented as autonomous award or ERP authorization
- **Procurement or business impact:** Creates unauthorized commercial or system action expectations.
- **Failure mode:** Recommendation language implies award, approval or ERP execution.
- **Authoritative component:** Governance classification and presentation.
- **Existing preventive control:** ADR-002 and ADR-003.
- **Existing test evidence:** Governance and public-presentation tests provide wording coverage; Gate 3B allocation screens and exports remain unverified.
- **Coverage state:** Partially Covered.
- **Required Gate 3B validation:** Assert recommendation-only labels and absence of ERP/award action semantics across UI and exports.
- **Severity / Likelihood / Detectability:** Critical / Medium / Easy.
- **Overall priority:** Blocker.
- **Blocking behaviour:** Any autonomous-award or authorization claim blocks merge.
- **Evidence required for closure:** UI/export text assertions and manual review.
- **Reverification triggers:** Workflow, ERP, export or recommendation language changes.
- **Owner or accountable role:** Procurement governance owner.

### TR-019 — Estimated savings are presented as realized savings
- **Procurement or business impact:** Misstates financial performance and damages credibility.
- **Failure mode:** Modeled opportunity is labelled realized or booked savings.
- **Authoritative component:** Executive outputs and governance wording.
- **Existing preventive control:** ADR-003 and portfolio limitation controls.
- **Existing test evidence:** Public-presentation and governed-recommendation tests provide partial wording coverage.
- **Coverage state:** Partially Covered.
- **Required Gate 3B validation:** Verify all allocation savings outputs retain estimate/opportunity classification.
- **Severity / Likelihood / Detectability:** High / Medium / Easy.
- **Overall priority:** High.
- **Blocking behaviour:** Unsupported realized-savings claim blocks merge.
- **Evidence required for closure:** UI/export assertions and manual content review.
- **Reverification triggers:** Savings calculation, export or executive wording changes.
- **Owner or accountable role:** Procurement finance owner.

### TR-020 — UI, intelligence and exports consume different allocation results
- **Procurement or business impact:** Stakeholders receive inconsistent sourcing recommendations.
- **Failure mode:** Consumers invoke different engines, snapshots or transformations.
- **Authoritative component:** Shared allocation result contract.
- **Existing preventive control:** ADR-001 and ADR-006.
- **Existing test evidence:** Existing export and download consistency tests cover other routes; no Gate 3B allocation consumer-identity test exists.
- **Coverage state:** Gap.
- **Required Gate 3B validation:** Build one result fixture and assert identical version, selected suppliers, shares and status across all consumers.
- **Severity / Likelihood / Detectability:** Critical / Medium / Difficult.
- **Overall priority:** Blocker.
- **Blocking behaviour:** Any consumer divergence blocks merge.
- **Evidence required for closure:** Cross-consumer reconciliation test and export snapshot.
- **Reverification triggers:** UI, intelligence, export or orchestration changes.
- **Owner or accountable role:** Integration architect.

### TR-021 — Export schema diverges from authoritative result contract
- **Procurement or business impact:** Downloaded evidence may not support the visible decision.
- **Failure mode:** Export omits, renames or recalculates critical fields inconsistently.
- **Authoritative component:** Allocation result contract and export adapter.
- **Existing preventive control:** ADR-001 and export integrity governance.
- **Existing test evidence:** `tests/test_export_integrity.py`, `tests/test_download_consistency.py` and scenario export tests provide general coverage; Gate 3B allocation schema is not direct.
- **Coverage state:** Partially Covered.
- **Required Gate 3B validation:** Contract-to-export field mapping, exact selected suppliers/shares/status/version and warning preservation.
- **Severity / Likelihood / Detectability:** High / Medium / Easy.
- **Overall priority:** High.
- **Blocking behaviour:** Missing or inconsistent authoritative fields block export acceptance.
- **Evidence required for closure:** Schema test and file-content reconciliation.
- **Reverification triggers:** Result contract or export schema changes.
- **Owner or accountable role:** Export owner.

### TR-022 — Category-specific evidence is lost during common-route normalization
- **Procurement or business impact:** Qualification rationale becomes incomplete or misleading.
- **Failure mode:** Common adapter drops required category evidence.
- **Authoritative component:** Category authorities and adapter evidence map.
- **Existing preventive control:** ADR-001, ADR-004 and ADR-007.
- **Existing test evidence:** Adapter tests preserve category evidence and normalize supported types; complete Gate 3B consumer preservation is not verified.
- **Coverage state:** Partially Covered.
- **Required Gate 3B validation:** Cross-category fixtures asserting required evidence survives route, result and presentation.
- **Severity / Likelihood / Detectability:** Critical / Medium / Difficult.
- **Overall priority:** Blocker.
- **Blocking behaviour:** Loss of mandatory category evidence blocks recommendation readiness.
- **Evidence required for closure:** Category-specific route tests for Steel, packaging and uploaded RFQ cases.
- **Reverification triggers:** Category aliases, adapter allowlist or route schema changes.
- **Owner or accountable role:** Category engine owners.

### TR-023 — Steel or another category bypasses the common governed route
- **Procurement or business impact:** Category outputs may avoid shared constraints and governance.
- **Failure mode:** Category-specific path presents allocation without adapter and shared engine.
- **Authoritative component:** Application route, common adapter and shared engine.
- **Existing preventive control:** ADR-001 and ADR-006.
- **Existing test evidence:** Engine cross-category tests and Steel adapter alias tests exist; application-route enforcement is incomplete.
- **Coverage state:** Partially Covered.
- **Required Gate 3B validation:** Parameterized route tests for Steel and representative categories proving adapter and engine versions.
- **Severity / Likelihood / Detectability:** Critical / Medium / Medium.
- **Overall priority:** Blocker.
- **Blocking behaviour:** Any visible category bypass blocks merge.
- **Evidence required for closure:** Route invocation evidence and version assertions.
- **Reverification triggers:** Category routing or Steel integration changes.
- **Owner or accountable role:** Application route owner.

### TR-024 — Application-route failure silently falls back to legacy logic
- **Procurement or business impact:** A failed governed route may still produce an apparently valid recommendation.
- **Failure mode:** Exception or blocked adapter state triggers legacy allocation without disclosure.
- **Authoritative component:** Application orchestration and status contract.
- **Existing preventive control:** ADR-001, ADR-006 and fail-closed governance.
- **Existing test evidence:** Adapter and engine failures are covered in isolation; no Gate 3B fallback test exists.
- **Coverage state:** Gap.
- **Required Gate 3B validation:** Inject adapter/engine failures and assert blocked state with no legacy result invocation.
- **Severity / Likelihood / Detectability:** Critical / Medium / Difficult.
- **Overall priority:** Blocker.
- **Blocking behaviour:** Any silent fallback blocks merge.
- **Evidence required for closure:** Mock/spy route tests and visible failure-state evidence.
- **Reverification triggers:** Exception handling, compatibility or route changes.
- **Owner or accountable role:** Application architect.

### TR-025 — Warning, blocked and failure statuses are not visible to users
- **Procurement or business impact:** Users may treat incomplete or infeasible analysis as actionable.
- **Failure mode:** Status is dropped, minimized or shown only in raw data.
- **Authoritative component:** Result and adapter status contracts plus UI presenter.
- **Existing preventive control:** Verification policy and ADR-004/006.
- **Existing test evidence:** Status codes are heavily tested; UI visibility tests exist for other modules but not the complete Gate 3B state matrix.
- **Coverage state:** Partially Covered.
- **Required Gate 3B validation:** UI tests for ready, warning, blocked, invalid input, infeasible and indeterminate states; manual browser check.
- **Severity / Likelihood / Detectability:** High / Medium / Easy.
- **Overall priority:** High.
- **Blocking behaviour:** Blocker states must be prominent and suppress recommendations.
- **Evidence required for closure:** State-matrix tests and screenshots.
- **Reverification triggers:** Status schema, UI components or wording changes.
- **Owner or accountable role:** UX and governance owners.

### TR-026 — Tests validate mechanics but miss procurement consequences
- **Procurement or business impact:** Green CI may coexist with commercially unsafe behaviour.
- **Failure mode:** Tests assert function execution without eligibility, capacity, currency, approval or decision consequences.
- **Authoritative component:** Definition of Done and this register.
- **Existing preventive control:** `DEFINITION_OF_DONE.md` and business-risk validation principle.
- **Existing test evidence:** Strong engine tests include procurement outcomes; Gate 3B risk-to-test mapping is not yet implemented.
- **Coverage state:** Partially Covered.
- **Required Gate 3B validation:** Every focused Gate 3B test must cite one or more register risk IDs in test documentation or governed review mapping.
- **Severity / Likelihood / Detectability:** High / Medium / Difficult.
- **Overall priority:** High.
- **Blocking behaviour:** Material blocker risks without direct consequence tests block merge.
- **Evidence required for closure:** Risk-to-test matrix and governed review.
- **Reverification triggers:** New tests, route scope or risk changes.
- **Owner or accountable role:** Test architect and procurement risk lead.

### TR-027 — Duplicate tests add maintenance cost without risk coverage
- **Procurement or business impact:** Slower change and false confidence from test volume.
- **Failure mode:** New tests repeat existing assertions at the same boundary.
- **Authoritative component:** Simplicity Gate and test architecture.
- **Existing preventive control:** `SIMPLICITY_GATE.md` and this register.
- **Existing test evidence:** No executable test is appropriate for preventing duplication; governed review is the control.
- **Coverage state:** Deferred with Rationale.
- **Required Gate 3B validation:** Review each proposed test against existing evidence and require a distinct risk, boundary or failure mode.
- **Severity / Likelihood / Detectability:** Medium / Medium / Easy.
- **Overall priority:** Medium.
- **Blocking behaviour:** Duplicate tests are rejected unless their distinct value is documented.
- **Evidence required for closure:** Review mapping and concise rationale.
- **Reverification triggers:** Test-suite expansion or duplicated fixtures.
- **Owner or accountable role:** Test architect.

### TR-028 — Documentation-only change is burdened with invented code tests
- **Procurement or business impact:** Governance becomes slow and ceremonial without added assurance.
- **Failure mode:** Pure Markdown change requires unrelated focused code tests.
- **Authoritative component:** `DEFINITION_OF_DONE.md`.
- **Existing preventive control:** Documentation-only DoD and full configured CI requirement.
- **Existing test evidence:** Gates 0B–0D use existing full CI without invented focused tests.
- **Coverage state:** Covered.
- **Required Gate 3B validation:** Not applicable to executable Gate 3B; retain rule for future documentation-only gates.
- **Severity / Likelihood / Detectability:** Medium / Low / Easy.
- **Overall priority:** Medium.
- **Blocking behaviour:** Reject unrelated test creation for documentation-only scope.
- **Evidence required for closure:** Changed-file boundary and configured CI result.
- **Reverification triggers:** DoD or workflow changes.
- **Owner or accountable role:** Governance lead.

### TR-029 — Hosted smoke success is misrepresented as browser/mobile certification
- **Procurement or business impact:** Readiness and usability claims exceed evidence.
- **Failure mode:** Startup smoke is described as browser, responsive, accessibility or mobile acceptance.
- **Authoritative component:** Verification policy and manual validation evidence.
- **Existing preventive control:** Portfolio classification and verification evidence rules.
- **Existing test evidence:** `tests/test_hosted_runtime_mobile_readiness.py` and smoke checks cover selected technical readiness, but smoke alone is not certification.
- **Coverage state:** Partially Covered.
- **Required Gate 3B validation:** Separate automated smoke from manual browser/mobile checks and record device/browser context where required.
- **Severity / Likelihood / Detectability:** High / Medium / Easy.
- **Overall priority:** High.
- **Blocking behaviour:** Unsupported certification language blocks closure claims, not necessarily code merge unless acceptance requires browser validation.
- **Evidence required for closure:** CI smoke evidence plus scoped manual acceptance record.
- **Reverification triggers:** Hosted route, responsive UI or browser-support claims.
- **Owner or accountable role:** Verification owner.

### TR-030 — Gate 3B changes an accepted ADR without reverification
- **Procurement or business impact:** Implementation silently departs from governed architecture.
- **Failure mode:** Engine ownership, approval, eligibility, currency, allocation, precedence or trace boundary changes without ADR review.
- **Authoritative component:** `docs/adr/README.md`, ADR-001 through ADR-008 and `VERIFICATION_POLICY.md`.
- **Existing preventive control:** ADR reverification triggers and change control.
- **Existing test evidence:** This is primarily a governed-review control; exact Git/CI evidence validates affected implementation.
- **Coverage state:** Covered.
- **Required Gate 3B validation:** Review changed files against all eight ADR triggers and record affected/not-affected determination.
- **Severity / Likelihood / Detectability:** Medium / Low / Medium.
- **Overall priority:** Medium.
- **Blocking behaviour:** Unreviewed conflict with an accepted ADR blocks merge.
- **Evidence required for closure:** ADR impact statement in governed review.
- **Reverification triggers:** Any Gate 3B architecture or authority change.
- **Owner or accountable role:** Architecture governance lead.

## Summary

### Priority counts

| Priority | Count |
|---|---:|
| Blocker | 19 |
| High | 8 |
| Medium | 3 |
| Low | 0 |
| **Total** | **30** |

### Coverage counts

| Coverage state | Count |
|---|---:|
| Covered | 11 |
| Partially Covered | 12 |
| Gap | 6 |
| Not Applicable | 0 |
| Deferred with Rationale | 1 |
| **Total** | **30** |

## Gate 3B merge blockers

The following risk IDs must have direct closure evidence before Gate 3B merge:

`TR-001`, `TR-002`, `TR-003`, `TR-004`, `TR-005`, `TR-006`, `TR-008`, `TR-009`, `TR-011`, `TR-012`, `TR-013`, `TR-014`, `TR-015`, `TR-017`, `TR-018`, `TR-020`, `TR-022`, `TR-023`, `TR-024`.

Existing component evidence may be reused only where it directly covers the unchanged boundary and no later change invalidates it. Gate 3B must add only the missing route, consumer, presentation and failure-boundary evidence.

## Manual versus automated evidence

- **Automated CI sufficient:** deterministic engine semantics, contract validation, missing/invalid inputs, exactly-K, capacity feasibility, tie-breaking and serialization where directly tested.
- **Automated route/UI tests required:** authoritative result identity, no legacy fallback, display-currency invariance, precedence, evidence-origin preservation, status visibility and export reconciliation.
- **Manual browser validation required:** visual prominence of warnings and approval boundaries, partial-evidence labelling, responsive display and any browser/mobile acceptance claim.
- **Smoke only:** confirms Streamlit startup and basic runtime availability; it does not certify complete browser, mobile, accessibility, security or production readiness.

## Maintenance rule

Update this register only when risk, authority, coverage, evidence or blocking treatment changes. Reference executable tests and governed CI rather than copying assertions. Do not mark a risk Covered based on analogous behaviour, test count or undocumented inference.