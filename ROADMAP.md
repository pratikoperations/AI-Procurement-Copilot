# Roadmap

## Portfolio Edition v1.0 — Packaging Procurement Engine

### Build 0.1 — Repository Foundation

- Repository structure
- Project governance
- Build rules
- Recovery documentation
- Initial app skeleton

### Build 0.2 — Streamlit Framework

- Modular app entry point
- Page layout
- Navigation
- Sidebar assumptions
- Basic synthetic data loading

### Build 0.3 — Procurement Engines

- Packaging should-cost engine
- Advanced TCO engine
- Structured supplier risk engine
- ESG scorecard
- Supplier performance scorecard

### Build 0.4 — Decision Intelligence

- Supplier ranking
- Lowest-price vs best-value logic
- Allocation recommendation
- What-if simulation
- Scenario stress testing

### Build 0.5 — Executive Outputs

- Executive dashboard
- Negotiation simulator
- Negotiation playbook
- Supplier clarification email
- Executive memo
- AI explainability panel
- Interview talking points

### Release v1.0 — Portfolio Edition

- Final documentation
- Screenshots
- User guide
- Interview guide
- Resume bullets

## Future Releases

### Version 1.1 — Time-Aware Procurement Analytics

**Status:** Approved backlog item; implementation deferred until after v1.0 release.

Planned capabilities:

- Global reporting-period context
- All Available Data and Custom Date Range modes
- Current month, quarter, and year presets
- Previous-quarter and previous-year comparisons
- Period-over-period, quarter-over-quarter, and year-over-year analysis
- Rolling 3-month and rolling 12-month trends
- Module-specific governing date fields
- Incomplete-period and missing-date warnings
- Reporting-period metadata in screens and exports
- Snapshot-versus-history distinction

Priority modules:

- RFQ analysis
- Supplier performance
- Supplier Relationship Management
- Spend analytics
- Savings tracking
- Supplier risk
- ESG and innovation
- Contract management
- Commodity-cost trends
- Procurement operations
- Supplier development

Required future components:

- `modules/date_context.py`
- `modules/period_comparison.py`
- `modules/time_series_validator.py`
- `modules/trend_analytics.py`

Estimated effort:

- 20–35 hours for a focused first release
- 40–70 hours for broad module coverage

See `docs/FUTURE_TIME_AWARE_ANALYTICS.md` for architecture, data prerequisites, safeguards, and acceptance criteria.

### Future Raw Material Enhancements

- Expanded commodity index logic
- Additional raw material should-cost models
- Advanced price indexation
- Commodity volatility analytics

### Version 2.0 — Multi-Category Procurement Platform

- Multiple configurable category engines
- Stronger validation
- Optional AI API layer
- Deployment package
