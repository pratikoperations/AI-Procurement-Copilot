# ERP Data Gap Analysis

## Status

Version 1.1 planning only. No application implementation is authorized by this document.

## Executive Conclusion

SAP or Oracle exports can support a large part of RFQ analysis, spend, delivery, invoice, contract, and supplier-performance intelligence. They usually cannot, by themselves, provide a complete should-cost model, verified ESG maturity, innovation maturity, financial resilience, supplier relationship quality, or market-index context.

The target design must therefore distinguish three evidence classes:

1. ERP-derived data
2. Manual or business-owned data
3. External market or third-party data

## Coverage by Module

| Copilot module | ERP coverage | Main gaps | Required supplement |
|---|---:|---|---|
| RFQ comparison | High | Technical compliance, negotiation context | Sourcing-team inputs |
| TCO | Medium to High | Hidden freight, inventory assumptions, switching cost | Manual assumptions and logistics data |
| Should-cost | Low to Medium | Commodity index, conversion rate, scrap, overhead, margin | External market data and category models |
| Supplier performance | High if maintained | Service and responsiveness may be subjective | Scorecard inputs |
| Supplier 360 | Medium | Financial, ESG, innovation, relationship evidence | Third-party and manual evidence |
| SRM | Medium | Strategic importance and relationship quality | Procurement review |
| Contract management | High if contract data is maintained | Obligation interpretation and legal risk | Contract review |
| Risk management | Medium | Geopolitical, financial, cyber, sanctions, capacity risk | External risk sources |
| Negotiation intelligence | Medium | BATNA, supplier cost structure, market leverage | Category strategy and external benchmarks |
| Time-aware analytics | High for transactions | Snapshot-only scorecards and missing dates | Historical extracts and dated assessments |

## 1. Data Commonly Available from SAP or Oracle

### Supplier Master

Typically available:

- Supplier ID
- Supplier name
- Address and country
- Active or blocked status
- Tax identifiers
- Payment terms
- Default currency
- Purchasing organization or business unit
- Category or commodity assignment where maintained

Reliability concerns:

- Duplicate supplier accounts
- Parent-child relationships missing
- Inconsistent legal names
- Old or inactive records
- Local and global IDs not aligned

### RFQ and Quote Data

Typically available:

- RFQ number
- Supplier
- Material or item
- Quote price
- Currency
- Quantity
- Unit
- Validity date
- Payment terms
- Lead time
- Incoterms

Potential gaps:

- Supplier assumptions behind price
- Technical compliance
- Tooling and one-time charges
- Cost breakdown
- Negotiation history
- Alternative specifications

### Purchase Orders

Typically available:

- PO number and line
- Supplier and material
- Order date
- Quantity
- Unit price
- Currency
- Unit
- plant or business unit
- contract reference
- release status

Potential gaps:

- True landed cost
- Off-system purchases
- Demand forecast
- Supplier capacity
- Reason for price variance

### Receipts

Typically available:

- Receipt date
- Received quantity
- PO linkage
- promised date or need-by date
- accepted and rejected quantity where quality integration exists

Potential gaps:

- Root cause of delay
- Carrier responsibility
- partial-delivery reason
- urgency or business impact

### Invoices

Typically available:

- Invoice number and date
- Supplier
- PO reference
- amount and currency
- quantity and price
- freight and tax where separately captured
- payment date or status

Potential gaps:

- Non-PO invoices
- hidden surcharges
- dispute history
- reason for price mismatch

### Quality

Available when quality modules are used:

- inspection lots
- accepted and rejected quantities
- defects
- quality notifications
- corrective actions

Potential gaps:

- Severity normalization
- customer impact
- cost of poor quality
- root-cause quality
- closure effectiveness

### Supplier Performance

Available when supplier evaluation is actively maintained:

- delivery score
- quality score
- service score
- overall score
- review period

Potential gaps:

- inconsistent scoring across plants
- overwritten historical scores
- missing evidence
- subjective ratings
- poor review frequency

### Contracts

Typically available:

- agreement number
- supplier
- dates
- price
- quantity
- terms
- status

Potential gaps:

- legal obligations
- renewal risk
- clause-level compliance
- rebates and complex pricing
- termination conditions

### Material Master

Typically available:

- item or material ID
- description
- unit
- material group or category
- standard cost
- specification references

Potential gaps:

- clean category taxonomy
- specification detail
- weight-per-piece conversion
- grade and composition
- obsolete materials

## 2. Data Usually Requiring Manual Entry or Business Ownership

### SRM and Relationship Inputs

Examples:

- Strategic importance
- Relationship quality
- Executive sponsorship
- Dependency level
- Joint business-plan status
- Supplier development plan
- Escalation status
- Collaboration maturity
- Exit or develop recommendation

Why manual:

These are management judgments and are rarely captured consistently in transactional ERP data.

### Technical and Commercial RFQ Context

Examples:

- Technical compliance
- Qualification status
- Approved specification
- Tooling ownership
- Switching cost
- Transition timeline
- Negotiation concessions
- BATNA
- Walk-away threshold

Why manual:

These depend on sourcing strategy and cross-functional judgment.

### Should-Cost Assumptions

Examples:

- Scrap rate
- Conversion cost
- Machine rate
- Labour rate
- Energy consumption
- Overhead
- Supplier margin
- Yield
- Packaging configuration

Why manual:

ERP standard cost is not the same as supplier should-cost and may use internal accounting logic.

### ESG and Innovation Evidence

Examples:

- Certification validity
- PCR content
- EPR compliance
- decarbonization plan
- innovation pipeline
- pilot outcomes
- value delivered

Why manual:

Evidence may exist in questionnaires, audits, certificates, or supplier presentations rather than ERP.

## 3. Data Usually Requiring External Market Sources

### Commodity and Cost Indices

Examples:

- Resin
- paper
- aluminium
- steel
- energy
- freight
- labour
- foreign exchange

Required fields:

- source name
- effective date
- geography
- currency
- unit
- confidence
- licensing or access restrictions

### Financial and Risk Data

Examples:

- credit rating
- bankruptcy risk
- financial statements
- sanctions
- geopolitical risk
- cyber risk
- weather and disruption risk

Important control:

External indicators must not be presented as verified facts without source and date metadata.

### Market Benchmarks

Examples:

- benchmark price
- supplier-market capacity
- industry lead time
- peer performance
- cost inflation

Important control:

Benchmarks must be comparable by period, geography, specification, unit, and currency.

## Gap Severity Framework

### Blocking Gap

Prevents the module from producing a safe decision.

Examples:

- Missing supplier ID
- Missing material ID
- Missing quote price
- Missing currency
- Missing unit
- incompatible units with no conversion

### Material Gap

Allows analysis but requires a prominent warning or provisional status.

Examples:

- Missing payment terms
- Missing lead time
- Missing quality evidence
- missing performance history
- missing contract status

### Enhancement Gap

Reduces detail but does not materially invalidate the core result.

Examples:

- Missing supplier parent
- Missing innovation narrative
- missing executive sponsor

## Missing-Data Response by Module

| Module | Blocking examples | Provisional examples | Default policy |
|---|---|---|---|
| RFQ | Price, currency, unit, supplier | lead time, MOQ, payment terms | Defaults visible and confidence reduced |
| TCO | normalized price, quantity | freight, inventory rate | Do not hide assumptions |
| Should-cost | category and core cost driver | overhead, scrap, margin | Use scenario range, not false precision |
| Supplier 360 | supplier identity | financial, ESG, innovation evidence | Cap scores and label evidence quality |
| SRM | supplier identity | relationship evidence | Human review required |
| Contract | contract ID and dates | renewal and notice terms | Flag incomplete record |
| Performance | supplier and period | missing sub-metrics | Calculate only supported metrics |

## Historical Data Gaps

Common problems:

- Only current supplier score retained
- RFQ history deleted or archived separately
- Invoices and receipts extracted for different periods
- supplier IDs changed after migration
- material descriptions changed
- currency rates not retained
- old units differ from current units
- records lack effective dates

Required controls:

- Display data coverage by sheet.
- Do not compare periods with incompatible scope.
- Keep migration cross-reference tables.
- Separate snapshot from event data.
- Exclude undated records from trend analysis and disclose the count.

## ERP-Specific Customization Risk

SAP and Oracle implementations are heavily customized. Risks include:

- Custom fields
- custom reports
- local code lists
- multiple business units
- multiple supplier numbering systems
- custom approval workflows
- ERP data replicated into data warehouses

Mitigation:

- Use mapping profiles.
- Require a data dictionary.
- Run a profiling report before ingestion.
- Preserve unmapped columns.
- Require human approval for mapping changes.

## Recommended MVP Scope

For the first ERP-upload release, prioritize:

1. Supplier Master
2. RFQ Quotes
3. Purchase Orders
4. Receipts
5. Supplier Performance
6. Material Master
7. Cost Drivers

Defer advanced invoice, contract, and quality integration only when time is constrained.

Why:

These seven sheets deliver most of the value for RFQ, supplier comparison, TCO, performance, Supplier 360, and should-cost preparation.

## Business Value and Effort

### ERP Export Upload

- Business value: High
- Adoption maturity: Mainstream
- Implementation effort: Medium
- Career relevance: 10/10
- Recommended action: Master

### Direct ERP API Integration

- Business value: High in production
- Adoption maturity: Scaling
- Implementation effort: High
- Career relevance: 7/10 for a procurement professional
- Recommended action: Monitor until file-based ingestion is stable

## Acceptance Criteria for Closing the Gap

- Every field is classified as ERP, manual, external, or derived.
- Missing-data consequences are defined.
- Source and effective-date metadata are retained.
- Supplier and material matching exceptions are visible.
- The system does not fabricate unavailable evidence.
- Should-cost clearly distinguishes ERP values from assumptions and market data.
- Supplier 360 caps or qualifies conclusions when evidence is incomplete.
- Historical coverage is disclosed by module.
- Mapping profiles are approved and versioned.
