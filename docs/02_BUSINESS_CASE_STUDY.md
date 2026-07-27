# AI Procurement Copilot v1.2 — Business Case Study

## 1. Business problem

Supplier evaluations are often distributed across spreadsheets, emails and individual judgement. Quotations may use different currencies, units and commercial assumptions. Lowest price can be mistaken for best value, while delivery, quality, risk and evidence gaps are not consistently reflected in the recommendation.

## 2. User and workflow

The primary user is a procurement or category professional conducting an RFQ evaluation. The user selects category assumptions, loads synthetic or RFQ data, reviews validation findings, compares suppliers, tests scenarios, prepares negotiation actions and produces executive outputs. Final approval remains outside the application.

## 3. Solution overview

AI Procurement Copilot structures this journey into a governed Streamlit application. Deterministic modules handle validation, comparison, should-cost, TCO, risk, scoring, allocation and recommendation eligibility. Business-facing views explain the result, while machine-readable files preserve audit detail.

## 4. Decision journey

1. Establish category, commodity, volume, currency and scenario assumptions.
2. Load data and preserve original source values.
3. Validate required fields, structure, units, currency and business rules.
4. Normalize the comparison basis using governed rules already implemented in the frozen baseline.
5. Compare lowest price, total cost, risk, performance, ESG and commercial factors.
6. Review scenario, allocation and negotiation implications.
7. Withhold award-oriented language when validation or evidence is insufficient.
8. Export review material for human procurement action.

## 5. Key application views

- Decision Summary
- Cost and Risk
- Scenarios and Negotiation
- Procurement Intelligence
- Supplier Intelligence
- Executive Outputs
- Downloads
- Separate ERP Upload Preview page

## 6. Governance and validation

The application preserves original and normalized quotation fields, exposes comparison assumptions and blocks unsupported currencies. Recommendation language is controlled by validation and eligibility status. Machine-readable outputs are separated from business-readable reports. Human approval remains mandatory.

## 7. What the project proves

- Understanding of procurement decision workflows
- Ability to build a functioning sourcing-analysis application
- Category-aware logic and visible assumptions
- Controlled validation and recommendation gates
- Modular architecture and automated testing
- Release, scope and claim governance

## 8. What it does not prove

- Live enterprise adoption
- Realized savings
- Production security or scalability
- Live SAP or Oracle connectivity
- Universal ERP mappings
- Automated supplier or material matching
- Autonomous sourcing or write-back

## 9. Outcome and learning

The project’s main outcome is a defensible portfolio demonstration of AI-enabled procurement decision support. The strongest design lesson is that reliable procurement AI depends less on opaque automation and more on explicit assumptions, deterministic controls, evidence quality, explainability and human authority.