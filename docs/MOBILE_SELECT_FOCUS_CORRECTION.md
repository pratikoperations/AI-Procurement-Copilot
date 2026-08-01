# Mobile Select Focus Styling Correction

## Governed scope

- Repository: `pratikoperations/AI-Procurement-Copilot`
- Base main SHA: `d143b9f108655732ac1db8988959d51e3c39ae6c`
- Correction branch: `fix/mobile-select-focus-styling`
- Finding: `MOBILE-UX-02`

## Root cause

Streamlit/BaseWeb applied its primary-color focus border to the select container while the application-wide `:focus-visible` rule independently added a yellow outline to the inner combobox. In the sidebar, overflow clipping reduced the yellow outline to a vertical stripe, producing a misleading red-plus-yellow error appearance during normal selection.

## Correction contract

- Normal select state uses the neutral application border.
- Hover uses a subtle neutral border.
- Focus uses one blue container-level ring through `:focus-within`.
- The inner combobox does not render a second focus outline.
- Red is reserved for controls exposing `aria-invalid="true"`.
- Keyboard focus remains visible and distinct from validation state.
- No category logic, supplier data, scoring, scenarios, allocation, exports or deployment settings changed.

## Verification requirement

Automated CSS contract tests and full CI must pass. Final closure additionally requires a physical Android screenshot showing the open sidebar select box without the former red border and yellow stripe.