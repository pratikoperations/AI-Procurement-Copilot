# Base Build Plan Reference — AI Procurement Copilot V9.5

## Source

This reference document summarizes the uploaded base plan: `AI Copilot base build plan.docx`.

## Purpose

Use this file as the functional blueprint for the modular Portfolio Edition v1.0 build. The uploaded V9.5 plan is a monolithic Streamlit proof-of-concept. The current GitHub project converts that concept into a modular, recoverable, extensible procurement decision platform.

## Base Plan Identity

- Original concept: AI Procurement Copilot V9.5 Interview Demo
- Core positioning: transparent RFQ + packaging should-cost + advanced TCO + EMV risk + ESG + performance + scenario stress test + constraint allocation + negotiation + executive memo
- Build direction: preserve functional intent, improve architecture

## Feature Inventory from Base Plan

### Already Implemented by Build 0.3

- Modular Streamlit app foundation
- Synthetic packaging RFQ data
- RFQ upload loader
- Packaging should-cost model
- Advanced TCO model
- Structured supplier risk model
- ESG scoring
- Supplier performance scoring
- Weighted supplier scoring
- Executive dashboard basics
- Supplier comparison output
- TCO breakdown output

### Target for Build 0.4

- Lowest-price vs best-value decision logic
- Constraint-style supplier allocation
- Multi-scenario stress testing
- Negotiation simulator
- Negotiation playbook
- Executive value breakdown
- Recommendation confidence

### Target for Build 0.5

- Executive sourcing memo
- Supplier clarification email generator
- AI-style explainability panel
- Interview talking points
- Stronger executive narrative

### Target for Release v1.0

- Final documentation
- User guide
- Screenshots
- Interview guide polish
- Resume / LinkedIn bullets
- Stable portfolio release

## Design Translation Rule

The base plan should not be copied as a single large script. Every feature should be translated into modular files under `modules/`, with project status, changelog, and build history updated after each milestone.

## Governance Rule

The base plan is the reference blueprint. The GitHub repository remains the source of truth for production code and current build status.
