# Interview Guide

## Project Positioning

AI Procurement Copilot demonstrates how AI-ready procurement and supplier intelligence can improve sourcing quality, decision transparency, supplier governance, risk visibility and executive communication while keeping safety gates and human approval explicit.

## Interview Pitch

The project converts RFQ and supplier data into category-specific should-cost, TCO, risk, sourcing, allocation and Supplier 360 recommendations. Build 0.9.6 adds data-confidence scoring, recommendation eligibility, business-rule validation, adversarial testing and safe withholding of award language when data is inadequate.

It does not simply select the lowest price and it does not force a recommendation when critical data, capacity, currency, UOM or validation conditions fail.

## Recommended Demo Flow

1. Select Packaging Procurement or Raw Material Procurement.
2. Load demo data or upload an RFQ.
3. Open the Validation Assurance Gate.
4. Explain supplied, defaulted, missing-critical and inferred data.
5. Show eligibility status and business-rule checks.
6. Demonstrate lowest price versus best value.
7. Show category-specific should-cost, TCO and risk.
8. Open Procurement Intelligence for strategy, allocation, negotiation and scenarios.
9. Open Supplier Intelligence for Supplier 360 and SRM.
10. Demonstrate a blocked file and show that final award language is withheld.
11. Close with the model-risk statement and human-approval requirement.

## Strong Interview Answer

> I built an AI-enabled procurement decision-support platform that evaluates RFQs using category-specific should-cost, TCO, risk and supplier performance logic. I extended it into Supplier 360 intelligence and then added a validation-assurance layer. The system measures data completeness, checks business rules, validates allocation feasibility and decides whether a recommendation is eligible, conditional, provisional, insufficient or blocked. When critical data fails, it withholds the polished award narrative. That is important because responsible AI adoption is not just about generating recommendations; it is about knowing when the system should refuse to recommend.

## Validation Talking Points

- Green CI proves expected code paths; it does not prove business correctness.
- Formula, assumption and decision-rule registers make logic auditable.
- Data confidence measures completeness, not probability of correctness.
- Recommendation confidence measures score separation, not forecast accuracy.
- Mixed currency and UOM data is blocked until normalized.
- Allocation must total 100% and remain within supplier capacity.
- Supplier 360 defaults are visible and reduce confidence.
- Financial health is an indicator, not bankruptcy prediction.
- Gemini, Perplexity and human review findings must be dispositioned before release approval.

## Business Value

- Improves sourcing and supplier-management decision quality.
- Reduces lowest-price bias and false confidence.
- Prevents infeasible allocations and invalid comparisons.
- Makes data gaps, defaults, assumptions and trade-offs visible.
- Supports negotiation, supplier development, continuity and SRM planning.
- Demonstrates responsible, governed AI adoption.

## Career Relevance

This project supports positioning for:

- Procurement transformation
- Strategic sourcing
- Packaging procurement
- Raw-material procurement
- Category management
- Supplier relationship management
- Procurement excellence
- Procurement analytics
- AI governance in operations
- Digital procurement leadership
