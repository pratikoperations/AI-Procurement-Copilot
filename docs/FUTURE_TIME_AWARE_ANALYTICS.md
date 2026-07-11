# Future Time-Aware Procurement Analytics

## Status

Documentation-only backlog item for post-v1.0 development.

**Recommended target:** Version 1.1 — Time-Aware Procurement Analytics

**Release-freeze rule:** This document does not authorize any change to the current application, calculations, schemas, tests, or release behavior.

## Business Rationale

Procurement decisions are rarely meaningful as point-in-time snapshots alone. RFQ outcomes, supplier performance, SRM classification, spend, savings, risk, ESG maturity, innovation, contracts, commodity costs, operational efficiency, and supplier-development activity all need a defined reporting period to support trend analysis and year-on-year improvement.

The future capability should allow users to analyze all available dated records or select a period and compare it with a relevant prior period. Every screen and export must make the selected reporting context explicit.

## Intended Procurement Use Cases

| Module | Governing Date Field | Time-Based Use |
|---|---|---|
| RFQ analysis | RFQ Date or Quote Effective Date | Compare sourcing rounds, quote movement, and supplier competitiveness |
| Supplier performance | Performance Period | Track OTIF, quality, complaints, delivery, and service trends |
| Supplier Relationship Management | Review Date | Compare SRM classification and relationship-development progress |
| Spend analytics | Transaction Date | Analyze monthly, quarterly, and annual spend movement |
| Savings tracking | Savings Realization Date | Separate pipeline, negotiated, implemented, and realized savings |
| Supplier risk | Assessment Date | Detect deterioration or improvement in risk signals |
| ESG | ESG Assessment Date | Track evidence maturity and corrective-action closure |
| Innovation | Innovation Review Date | Track ideas, pilots, benefits, and collaboration progress |
| Contract management | Contract Start Date and Contract End Date | Review expiries, renewals, compliance, and leakage |
| Commodity cost trends | Index or Price Effective Date | Analyze index, premium, freight, duty, and FX movement |
| Procurement operations | Activity or Completion Date | Measure cycle time, workload, approvals, and turnaround |
| Supplier development | Action Review or Closure Date | Track corrective-action closure and performance recovery |

## Required User Experience

The future system should support:

- All Available Data
- Custom Date Range
- Current Month
- Current Quarter
- Current Year
- Previous Quarter
- Previous Year
- Period-over-period comparison
- Quarter-over-quarter comparison
- Year-over-year comparison
- Rolling 3-month analysis
- Rolling 12-month analysis

### No Date Range Selected

Use all available dated records and display:

- Earliest available date
- Latest available date
- Number of records included
- Number of undated records excluded
- Whether the dataset is historical or only a current snapshot

### Date Range Selected

Filter by the module-specific governing date and display:

- Selected period
- Comparison period
- Records included
- Records excluded
- Undated records excluded
- Data-completeness warning
- Whether the period is complete or partial

## Data Prerequisites

Every relevant record must have:

- A valid governing date
- Explicit date granularity where relevant
- Stable supplier, category, and event identifiers
- Comparable units and currencies
- Historical records rather than only one current snapshot
- Data-source metadata
- Effective-date or period-end logic

Dates must be normalized to a consistent internal representation. Missing dates must remain missing and must never be silently assigned to the current period.

## Required Schema Changes

Future schema work may add fields such as:

- RFQ Date
- Quote Effective Date
- Performance Period Start
- Performance Period End
- Transaction Date
- SRM Review Date
- Risk Assessment Date
- ESG Assessment Date
- Innovation Review Date
- Contract Start Date
- Contract End Date
- Savings Realization Date
- Commodity Price Effective Date
- Record Created Date
- Record Updated Date
- Reporting Period Type
- Source System

Schema migration must preserve backward compatibility and distinguish legacy snapshot records from historical records.

## Proposed Future Architecture

### `modules/date_context.py`

Responsibilities:

- Global date selection
- Preset periods
- Selected-period metadata
- Available-data coverage
- Module-specific date-field mapping

### `modules/period_comparison.py`

Responsibilities:

- Previous-period comparison
- Year-over-year and quarter-over-quarter logic
- Like-for-like period matching
- Percentage and absolute change calculations
- Suppression when comparison data is inadequate

### `modules/time_series_validator.py`

Responsibilities:

- Missing-date detection
- Invalid-date detection
- Duplicate-period checks
- Incomplete-period detection
- Minimum-record thresholds
- Coverage and comparability validation

### `modules/trend_analytics.py`

Responsibilities:

- Period aggregation
- Rolling 3-month and 12-month analysis
- Trend direction
- Volatility and change metrics
- Module-specific trend summaries

## Comparison Rules

- Do not generate a comparison when a valid prior period is unavailable.
- Do not compare incomplete and complete periods without a prominent warning.
- Use like-for-like calendar coverage for year-on-year analysis.
- Do not treat undated records as current-period data.
- Do not mix currencies or units across periods without governed normalization.
- Suppress percentage change when the baseline is zero or invalid.
- Show record counts and coverage quality next to every trend conclusion.
- Distinguish activity volume changes from performance-rate changes.

## Risks of False Precision

A date selector can create misleading confidence when:

- The underlying data is only a point-in-time snapshot
- Prior-period records are incomplete
- Different periods use different suppliers, units, currencies, or definitions
- Missing dates are excluded without disclosure
- Partial quarters are compared with complete quarters
- Small sample sizes produce unstable percentages
- Historical values were restated or overwritten

The system must refuse or qualify comparisons when these risks are material.

## Export Requirements

All relevant exports should include:

- Selected reporting period
- Comparison period
- Earliest and latest included dates
- Record count
- Excluded undated-record count
- Complete or partial-period status
- Governing date field
- Comparison method
- Validation warning

## Recommended Implementation Sequence

1. Define governing date fields and schema standards for every module.
2. Add date parsing, normalization, and validation utilities.
3. Add historical synthetic datasets for RFQ, performance, SRM, spend, and savings.
4. Implement `date_context.py` and the global reporting-period contract.
5. Implement module-level filtering using the declared governing date.
6. Implement period comparison and incomplete-period safeguards.
7. Add rolling-window trend analytics.
8. Add period metadata to all screens and exports.
9. Add regression, adversarial, and cross-period consistency tests.
10. Perform procurement-user validation before release.

## Estimated Effort

Estimated implementation effort: **20–35 hours** for a credible first release, assuming historical synthetic data and five priority modules.

A broader implementation covering every listed module may require **40–70 hours**, depending on schema migration, data quality, and export complexity.

## Recommended Priority

**Recommendation:** Learn and implement after v1.0 release.

**Business value:** High

**Implementation complexity:** Medium to High

**Adoption maturity:** Mainstream analytics practice

**Career relevance:** 9/10

## Acceptance Criteria

Version 1.1 should not be considered complete unless:

- Every enabled module declares its governing date field.
- All Available Data and Custom Date Range work consistently.
- Current, previous, and rolling periods are supported where valid.
- Screens and exports display reporting-period metadata.
- Missing and invalid dates are disclosed.
- Incomplete periods are labelled.
- Prior-period comparisons are suppressed when not comparable.
- YoY and QoQ calculations use like-for-like periods.
- Undated records are never silently reassigned.
- Snapshot and historical data are clearly distinguished.
- Unit and currency consistency is enforced across periods.
- Regression and adversarial tests pass.
- Human procurement review confirms the outputs are decision-useful.

## Current Release Boundary

Build 1.0 RC1.2.1 remains under release freeze. No date selector, historical calculation, schema change, or application behavior is introduced by this backlog record.