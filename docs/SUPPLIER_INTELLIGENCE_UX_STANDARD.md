# Supplier Intelligence UX Standard

## Audience

Procurement Manager, Category Manager, Strategic Sourcing Lead, Procurement Excellence Lead and Procurement Director.

## Presentation standard

Supplier Intelligence must present business meaning first and technical structure never.

Approved on-screen components:

- Metric cards
- Status cards
- Score bars
- Comparison matrices
- Tables
- Dimension charts
- Evidence lists
- Strength and gap panels
- Action plans
- Risk alerts
- Governance notes
- Executive summaries

Prohibited on-screen output:

- Raw JSON
- Python dictionaries or lists
- Code blocks
- Braces or quoted field names
- Snake-case labels
- Numeric list indexes
- Debug payloads
- Internal object representations

## Evidence governance

Every financial, ESG and innovation view must show:

- Assessment status
- Displayed score
- Data completeness
- Evidence quality
- Verification or due-diligence requirement
- Clear warning when evidence is incomplete

Raw scores may exist internally but cannot be presented as verified strength when evidence is weak.

## Mobile standard

- Use no more than three metric cards per row where practical.
- Allow Streamlit columns to stack naturally.
- Prefer focused supplier views over extremely wide matrices.
- Keep long tables downloadable.
- Use responsive Plotly charts.
- Avoid wide code or structured-data blocks.

## Downloads

Machine-readable audit files are download-only. Every machine-readable output should have a human-readable alternative when practical.
