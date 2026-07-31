# Hosted, Desktop and Mobile Verification — Governed Evidence

## Governed repository state

- Repository: `pratikoperations/AI-Procurement-Copilot`
- Authoritative main SHA at verification start: `d143b9f108655732ac1db8988959d51e3c39ae6c`
- Merged closure PR: `#34`
- PR #34 merge commit: `d143b9f108655732ac1db8988959d51e3c39ae6c`
- Hosted application identity from the authoritative README: `https://ai-procurement-copilot.streamlit.app/`
- Final verified merge-test evidence: Quality Checks run 751, run ID `30666074104`, job ID `91273299881`, merge-test SHA `76d7b0803972dc2b963b9448920e954412b03e54`
- Automated result: 849 tests passed; Python compilation passed; Streamlit smoke passed; one pre-existing pandas FutureWarning

## Verification method

The authorized review attempted to establish a hosted interactive browser session for desktop, narrow/mobile and Android-compatible journeys. The available execution environment could verify GitHub state, repository source, hosted application identity, automated CI evidence, route contracts and export contracts, but could not create an interactive browser or Android session against the public Streamlit host.

No desktop, mobile or Android pass is claimed without direct observed interaction.

## Structured evidence

| Viewport or device | Route | Expected result | Observed result | Status | Classification |
|---|---|---|---|---|---|
| Hosted endpoint | Application identity | Existing Streamlit application is identified without deployment change | Authoritative README identifies `https://ai-procurement-copilot.streamlit.app/` | Pass | Repository evidence |
| Hosted endpoint | Runtime reachability | Public host loads and exposes the application | Interactive host session could not be established from the verification environment | Not verified | Environment limitation |
| Desktop browser | Common navigation and category controls | Usable sidebar, category selection, volume and currency controls | No interactive desktop browser available | Not verified | Environment limitation |
| Narrow/mobile browser | Responsive containment and scrolling | Controls and tables remain usable without uncontrolled overflow | No interactive narrow viewport available | Not verified | Environment limitation |
| Android-compatible journey | Navigation and downloads | App interaction and governed downloads work on Android browser | No physical or emulated Android browser available | Not verified | Environment limitation |
| Automated merge-test | Full application regression | Category logic and contracts remain intact | 849 tests passed; compilation and Streamlit smoke passed | Pass | Automated evidence |

## Category verification status

### C1 — Kraft Paper

Automated and source-contract evidence confirms controlled variants, quantity basis, should-cost, technical eligibility, risk, scoring, governed recommendation, scenarios, allocation behavior where applicable, UX contracts, exports and claim boundaries.

Hosted desktop/mobile interaction remains unverified.

### C2 — Flexible Laminates

Automated and source-contract evidence confirms PET / PE, PET / MetPET / PE and BOPP / CPP structures, dependent print-profile state, technical eligibility, separate risk, governed recommendation, exactly seven scenarios, standard and optimized allocation, Excel and strict JSON contracts.

Hosted desktop/mobile interaction remains unverified.

### C3 — Steel Sheets and Coils

Automated and source-contract evidence confirms CR, GI Z120 and PPGI Z120 profiles; profile, sourcing-route and display-mode transitions; stale zinc, paint and duty clearing; eligibility before scoring; separate generic and Steel-specific risk; winner and no-winner behavior; exactly seven scenarios; standard and optimized allocation; unallocated volume; nine-sheet Excel; strict `steel_governance` JSON; and generic-output isolation.

Hosted desktop/mobile interaction and physical download behavior remain unverified.

## Download and export status

- Export generation and schema reconciliation are covered by automated tests.
- Excel and JSON download controls are present in source contracts.
- Physical browser download behavior, Android file handling and downloaded-file opening were not directly observed.

## Findings

### Blockers

1. No direct hosted browser session was available to verify the merged application user journey.
2. No narrow/mobile or Android browser session was available.

These are verification blockers, not confirmed application defects.

### Non-blocking known limitations

- No full browser-driven AppTest suite covers every category transition.
- Some generic computations occur before category-specific route termination.
- Supplier, market, FX, duty and capacity inputs remain controlled synthetic demonstration assumptions.
- The programme closure document contains historical pre-PR-34 main coordinates and should be read with this verification record.

## Readiness decision

- Engineering and automated-test readiness: **Pass**.
- Hosted endpoint identity: **Confirmed**.
- Desktop interactive readiness: **Not verified**.
- Mobile and Android readiness: **Not verified**.
- Final portfolio demonstration readiness: **Conditionally ready only after a real hosted desktop and mobile walkthrough is completed and recorded**.

No blocker-level application defect was confirmed. Portfolio readiness is withheld because required interactive evidence could not be produced in the available environment.

## Governance

No deployment, code, calculation, supplier data, scoring, scenario, allocation, UX, export, tag, release or branch-deletion action was performed during this verification phase.
