# Assumption Register

| Assumption | Default | Category | Justification | Source type | User-adjustable | Sensitivity | Risk of misuse |
|---|---:|---|---|---|---|---|---|
| Annual volume | 500,000 | Both | Enables annualized comparison in demo mode | Portfolio demo | Yes | High | Wrong volume distorts TCO, capacity and savings |
| USD–INR FX | 83 | Both | Display conversion baseline | Portfolio demo | Yes | Medium | Must not be treated as live FX |
| Raw-material shock | 0% | Both | Base scenario | User scenario | Yes | High | Shock is not forecast probability |
| Freight shock | 0% | Both | Base scenario | User scenario | Yes | Medium | Actual lane rates may differ |
| Demand change | 0% | Both | Base scenario | User scenario | Yes | High | Impacts capacity and annual TCO |
| Inventory carrying rate | 18% | Both | Simplified annual carrying-cost assumption | Model assumption | No in current UI | Medium | Must be calibrated to business finance policy |
| Cost of capital | 12% | Both | Simplified working-capital assumption | Model assumption | No in current UI | Medium | Not company-specific WACC |
| Maximum supplier share | 75% | Both | Maintains continuity in demo | User policy | Yes | High | May be inappropriate for constrained categories |
| Minimum backup share | 25% | Both | Preserves secondary source | User policy | Yes | High | Depends on qualification and capacity |
| Minimum risk score | 55 | Both | Prevents weak-risk supplier from unrestricted award | User policy | Yes | High | Threshold requires governance approval |
| Minimum ESG score | 50 | Both | Portfolio sustainability gate | User policy | Yes | Medium | Category-specific ESG materiality may differ |
| Supplier capacity fallback | MOQ ×20 or 100,000 minimum | Supplier 360 | Keeps demo profile operational when capacity is absent | Transparent default | No | High | Must never be treated as verified capacity |
| Capacity utilization fallback | 100 − capacity buffer | Supplier 360 | Approximate utilization indicator | Transparent inference | No | High | Not an audited production measure |
| Financial buyer dependency | 20% | Supplier intelligence | Enables demo health indicator | Transparent default | No | High | Real due diligence required |
| Financial revenue concentration | 35% | Supplier intelligence | Enables demo health indicator | Transparent default | No | High | Real financial data required |
| Responsiveness/service scores | 70 | Supplier performance | Neutral demo midpoint | Transparent default | No | Medium | Can overstate unknown service maturity |
| ESG social/governance fields | 70 | Supplier ESG | Neutral demo midpoint | Transparent default | No | High | Verified evidence required before ESG claims |
| Innovation fields | 45–65 | Supplier innovation | Enables maturity demonstration | Transparent default | No | High | Must not be presented as supplier fact |

## Policy

All assumptions must be visible, traceable and replaceable with verified business data before production use. Defaults are acceptable for portfolio demonstration only when clearly labelled and included in the data-confidence calculation.
