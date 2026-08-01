# Sidebar Information Architecture

## Objective

Reduce sidebar length and remove category-irrelevant controls without changing procurement calculations, supplier data, scenario logic, allocation logic, or export schemas.

## Control applicability

| Section | Kraft Paper | Flexible Laminates | Steel |
|---|---|---|---|
| Sourcing Setup | Visible | Visible | Visible |
| Category Inputs | Kraft controls | Material, printing, losses/tooling | Steel controls |
| Commercial Basis | Visible, collapsed | Visible, collapsed | Visible, collapsed |
| Generic Scenario Inputs | Visible, collapsed | Visible, collapsed | Hidden |
| Generic Allocation Rules | Visible, collapsed | Visible, collapsed | Hidden |
| About / Roadmap | Visible, collapsed | Visible, collapsed | Visible, collapsed |

Steel hides generic scenario and allocation controls because the dedicated Steel engine uses seven governed scenarios and dedicated allocation outputs. Backward-compatible default values remain in the returned assumptions contract.

## Default expansion state

- Sourcing Setup: always visible.
- Primary category inputs: expanded.
- Flexible Laminates printing: collapsed.
- Flexible Laminates process losses and tooling: collapsed.
- Commercial Basis: collapsed.
- Scenario Inputs: collapsed when applicable.
- Allocation Rules: collapsed when applicable.
- About / Roadmap: collapsed.

## Compatibility boundaries

- Existing widget keys are retained.
- Existing assumptions return keys are retained.
- Steel controls render once in the sidebar and the dashboard consumes the returned normalized state.
- No calculation, supplier, scenario, allocation, or export algorithm is changed.
- No production deployment change is included.
