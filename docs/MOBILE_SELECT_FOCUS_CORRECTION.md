# Mobile Select Focus Styling Correction

## Governed scope

- Repository: `pratikoperations/AI-Procurement-Copilot`
- Base main SHA: `d143b9f108655732ac1db8988959d51e3c39ae6c`
- Active correction branch: `fix/hosted-runtime-mobile-readiness`
- Pull request: `#37`
- Finding: `MOBILE-UX-02`

## Hosted evidence

Physical Android screenshots on Streamlit `1.59.1` showed that focused/open select controls still rendered a red outer treatment and a yellow vertical stripe after earlier descendant-selector corrections. The behavior reproduced on Commodity / Material, Steel Profile and Sourcing Route controls while the controls remained functionally usable.

## Rendered-DOM diagnosis

The generated component has two visual layers:

1. the immediate BaseWeb select control shell (`[data-baseweb="select"] > div`), which retains Streamlit's primary-color focused/open treatment; and
2. a nested focusable input, combobox or tabindex node, which inherits the application-wide focus token.

The nested focus indication is clipped at the trailing indicator boundary and appears as a narrow yellow vertical stripe. The red treatment is consistent with Streamlit's primary focus color reaching the immediate control shell. Live browser DevTools computed-style capture was not available in the execution environment, so this is a selector-level diagnosis grounded in the hosted screenshots and the active CSS cascade, not a claim of a captured computed-style trace.

## Final narrow correction contract

- The immediate BaseWeb control shell is the only visible owner of border and focus styling.
- The select wrapper locally remaps both the application focus token and Streamlit primary token to `--aipc-select-focus`.
- Default state uses the neutral application border.
- Hover uses a subtle neutral border.
- Focus/open state uses one blue control-shell ring.
- Nested input, combobox and tabindex nodes retain transparent outlines rather than `outline:none`.
- The trailing indicator shell cannot expose a colored left divider, outline or shadow.
- Red remains reserved for controls exposing `aria-invalid="true"`.
- Touch sizing, dropdown readability and all procurement logic remain unchanged.

## Exact selectors

Visual owner:

```css
[data-baseweb="select"] > div
```

Focused/open state:

```css
[data-baseweb="select"]:focus-within > div,
[data-baseweb="select"]:has([aria-expanded="true"]) > div
```

Nested focus neutralization:

```css
[data-baseweb="select"] :is(input, [role="combobox"], [tabindex]:not([tabindex="-1"]))
```

Trailing indicator neutralization:

```css
[data-baseweb="select"] > div > div:last-child
```

Invalid state:

```css
[data-baseweb="select"]:has([aria-invalid="true"]) > div,
[data-baseweb="select"] [role="combobox"][aria-invalid="true"]
```

## Governance boundary

No Steel routing, Steel state lifecycle, procurement calculations, supplier data, scenarios, allocation, exports, responsive metric layout, production deployment or release setting is changed by this final narrow correction.

## Verification requirement

Automated CSS contract tests and full CI must pass. Final closure additionally requires a physical Android screenshot showing an open select control with:

- no red valid-focus border;
- no yellow vertical stripe;
- one visible blue focus/open ring;
- readable selected value and dropdown options.
