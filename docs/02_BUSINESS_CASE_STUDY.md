# AI Procurement Copilot — Business Case Study

## 1. Business problem

Supplier evaluations are often distributed across spreadsheets, emails and individual judgement. Quotations may use different currencies, units and commercial assumptions. Lowest price can be mistaken for best value, while delivery, quality, risk and evidence gaps are not consistently reflected in the recommendation.

A second challenge is explainability: even when a procurement calculation is correct, reviewers may struggle to identify which assumptions, source functions, evidence and reconciliation checks support the result.

## 2. User and workflow

The primary user is a procurement or category professional conducting an RFQ evaluation. The user selects category assumptions, loads synthetic or sanitized RFQ data, reviews validation findings, compares suppliers, tests scenarios where supported, prepares negotiation actions and produces executive outputs.

Final procurement approval remains outside the application.

## 3. Solution overview

AI Procurement Copilot structures this journey into a governed Streamlit application.

For active analytical categories, deterministic modules handle validation, comparison, should-cost, TCO, risk, scoring, allocation and recommendation eligibility.

The governance layer adds:
- calculation catalogue and formula identity;
- assumption provenance;
- deterministic trace evidence;
- reconciliation status;
- explicit unavailable/deferred evidence states;
- read-only SourceMate access to governed project evidence;
- human-review boundaries.

## 4. Decision journey

1. Establish category, commodity, volume, currency and scenario assumptions.
2. Load synthetic or sanitized data and preserve original source values.
3. Validate required fields, structure, units, currency and business rules.
4. Normalize the comparison basis using governed rules.
5. Compare price, total cost, risk, performance, ESG and commercial factors where supported.
6. Review scenario, allocation and negotiation implications for active analytical categories.
7. Inspect calculation identity, assumptions, trace and reconciliation evidence.
8. Withhold or qualify recommendation language when validation/evidence is insufficient.
9. Export review material for human procurement action.

## 5. Current application scope

- Packaging procurement workflows
- Raw-material-style procurement workflows
- Steel as a non-packaging transferability example
- Governed Calculation Explorer
- SourceMate with chat-style UX and page-aware governed context
- Read-only ERP structural preview
- MRO / Industrial Supplies **Foundation Preview** using Industrial Bearings

## 6. MRO-0 business rationale

MRO sourcing is different from packaging and commodity raw materials because correct identity and technical compatibility can matter more than price-only comparison.

MRO-0 therefore focuses first on:
- manufacturer and part-number identity;
- source legitimacy;
- technical compatibility evidence;
- equivalent-part governance;
- human substitution approval.

This is intentionally a foundation-only capability. No MRO should-cost, scoring, scenario, negotiation or allocation engine is claimed.

## 7. Governance and validation

The application preserves original and normalized quotation fields, exposes comparison assumptions and blocks unsupported conditions. Recommendation language is controlled by validation and eligibility status.

Unavailable evidence is disclosed rather than reconstructed. SourceMate does not externally verify suppliers or evidence. Human approval remains mandatory.

## 8. What the project proves

- understanding of procurement decision workflows;
- ability to build a functioning sourcing-analysis application;
- category-aware logic and visible assumptions;
- controlled validation and recommendation gates;
- explainability without duplicate calculation engines;
- explicit provenance and evidence boundaries;
- extensible category architecture;
- modular design and automated testing;
- disciplined release, scope and claim governance.

## 9. What it does not prove

- live enterprise adoption;
- realized savings;
- production security or scalability;
- live SAP or Oracle connectivity;
- universal ERP mappings;
- external supplier verification;
- production-ready MRO analytics;
- autonomous sourcing, approval, award or ERP write-back.

## 10. Outcome and learning

The project’s main outcome is a defensible portfolio demonstration of AI-enabled procurement decision support.

The central design lesson is that credible procurement AI depends less on opaque automation and more on explicit assumptions, deterministic controls, evidence quality, explainability, bounded authority and human accountability.
