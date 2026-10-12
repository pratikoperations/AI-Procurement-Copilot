# AI Procurement Copilot — Executive Overview

## What it is

AI Procurement Copilot is a governed procurement decision-support portfolio application for RFQ comparison, sourcing evaluation and calculation explainability. It helps procurement professionals review supplier quotations beyond lowest price by making cost, risk, delivery, quality, commercial terms, evidence quality and decision boundaries visible.

The current product is a **portfolio/interview demonstrator under stabilization freeze**, not production enterprise software.

## Target users

- Procurement managers
- Category managers
- Strategic sourcing leads
- Procurement excellence teams
- Supplier relationship managers

## Core capabilities

1. **Governed supplier comparison** — validates quotation data and compares suppliers using visible category, currency, unit, cost and risk assumptions.
2. **Sourcing decision support** — supports scenarios, allocation, negotiation preparation and evidence-gated recommendation language for active analytical categories.
3. **Explainability and evidence** — provides governed calculation identities, assumption provenance, deterministic traces, reconciliation and evidence-boundary visibility.
4. **SourceMate** — provides project-wide, read-only, deterministic, chat-style access to governed application evidence without browsing, external LLMs, RAG, hidden recalculation or transaction authority.
5. **Category extensibility** — demonstrates bounded category expansion through the MRO / Industrial Supplies **Foundation Preview**, using Industrial Bearings as the first representative commodity.

## Business relevance

The project demonstrates how fragmented spreadsheet analysis can be converted into a repeatable, explainable procurement workflow while preserving human approval. It is relevant to strategic sourcing, category management, supplier risk, procurement analytics, procurement excellence and digital transformation.

## Current portfolio baseline

- Repository: `pratikoperations/AI-Procurement-Copilot`
- Hosted application: `https://ai-procurement-copilot.streamlit.app/`
- Current canonical `main`: `b7037fe21aa64aff799f38b911a6ed3e64d355c0`
- Latest governed category extension: MRO-0 / Industrial Supplies Foundation Preview
- Human procurement approval: mandatory
- Live ERP write-back: not implemented
- Autonomous supplier award: not implemented

## MRO-0 position

MRO-0 adds a governed foundation for Industrial Bearings with:
- manufacturer + manufacturer-part-number identity;
- OEM / Authorized Distributor / Approved Equivalent source status;
- technical, commercial, supplier and evidence contracts;
- fail-closed compatibility review;
- explicit human approval for equivalent substitution and supplier selection.

It intentionally does **not** activate MRO should-cost, scoring, scenario, negotiation or allocation execution.

## What the project proves

- practical procurement workflow understanding;
- ability to translate procurement requirements into working software;
- governed data validation and recommendation boundaries;
- explainability and evidence design;
- cross-category architecture;
- disciplined scope control;
- GitHub/CI governance and exact-head validation.

## What it does not prove

- production deployment readiness;
- enterprise-scale security, identity or monitoring;
- live SAP/Oracle integration;
- realized savings from live organizational adoption;
- external supplier evidence verification;
- autonomous sourcing, qualification, award or production allocation.

## Limitation statement

This is a portfolio demonstration. Synthetic or sanitized data should be used. Final procurement decisions remain with human reviewers.
