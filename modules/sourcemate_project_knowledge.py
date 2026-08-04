"""Governed project-wide knowledge registry for SourceMate.

The registry contains concise, repository-grounded explanations of existing
AI Procurement Copilot capabilities. It is documentation only: it does not
execute calculations, scoring, allocation, recommendations, or procurement
actions.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

PROJECT_KNOWLEDGE_CONTRACT = "AIPC-SOURCEMATE-PROJECT-KNOWLEDGE-1.0"


def _entry(
    topic: str,
    aliases: Sequence[str],
    answer: str,
    sources: Sequence[str],
    *,
    limitations: str = "Human procurement review remains mandatory.",
) -> dict[str, Any]:
    return {
        "topic": topic,
        "aliases": tuple(aliases),
        "answer": answer,
        "sources": tuple(sources),
        "limitations": limitations,
    }


PROJECT_KNOWLEDGE = (
    _entry(
        "project architecture and scope",
        ("project", "architecture", "scope", "portfolio", "what does this app do", "overview"),
        "AI Procurement Copilot is a read-only portfolio decision-support application. It combines RFQ ingestion, category engines, should-cost, TCO, risk, supplier intelligence, scenarios, governed recommendations, allocation evidence, exports, calculation trace, reconciliation and human-review controls. It does not claim production deployment, autonomous award, live ERP integration or realized savings.",
        ("README.md", "PROJECT_CONTROL.md", "app.py"),
    ),
    _entry(
        "category engines",
        ("category engine", "categories", "packaging", "raw material", "steel", "flexible laminate", "kraft", "pet resin"),
        "The portfolio includes Packaging Procurement, Raw Material Procurement and governed category-specific routes for Corrugated Board, Kraft Paper, PET Resin, Flexible Laminates and Steel. Category routing selects existing deterministic services; SourceMate does not create a new calculation route.",
        ("modules/category_engine.py", "modules/category_cost_router.py", "pages/8_Governed_Calculation_Explorer.py"),
    ),
    _entry(
        "flexible laminates supplier qualification",
        ("flexibles vendor", "flexible vendor", "flexibles supplier", "flexible laminates supplier", "qualified for flexibles", "vendor qualified for flexibles", "which vendor qualified"),
        "For the controlled synthetic Flexible Laminates demonstration, Precision Flexibles Ltd and BarrierPack Films are technically eligible under the registered application-approval, capability, continuity, utilisation and substrate-availability controls. Circular Laminate Solutions is treated as technically ineligible in the governed decision path because its continuity and operating-risk evidence breaches registered thresholds.\n\n| Supplier | Governed demo status | Explanation |\n|---|---|---|\n| Precision Flexibles Ltd | Eligible | Approved application with qualifying capability and continuity evidence. |\n| BarrierPack Films | Eligible | Approved application with qualifying capability and continuity evidence. |\n| Circular Laminate Solutions | Ineligible | Fails registered technical continuity or risk thresholds in the controlled demo. |\n\nThese are synthetic portfolio records, not audited supplier qualification or a production award decision.",
        ("modules/data_loader.py::get_flexible_laminate_demo_suppliers", "modules/flexible_laminate_risk.py::assess_flexible_laminate_supplier", "tests/test_c2_decision_path.py"),
    ),
    _entry(
        "should-cost methodology",
        ("should cost", "should-cost", "cost formula", "target cost", "cost breakdown"),
        "Should-cost outputs are produced by existing deterministic category services. The Governed Calculation Explorer presents the authoritative result, registered assumptions, trace and reconciliation. Formula metadata is explanatory and non-executable; SourceMate only explains existing outputs.",
        ("modules/should_cost.py", "modules/raw_material_cost.py", "modules/flexible_laminate_cost.py", "modules/steel_cost.py"),
    ),
    _entry(
        "total cost of ownership",
        ("tco", "total cost", "total cost of ownership", "tco percentage", "tco parameter", "freight exposure", "inventory carrying"),
        "The packaging TCO model starts from quoted unit price and separately adds scenario price exposure, freight, inventory carrying cost, working-capital impact, risk penalty and a lead-time buffer. Default parameters are: raw-material exposure 60%, cost of capital 12%, inventory carrying rate 18%, maximum freight exposure 6%, maximum failure probability 20%, and business-impact multiplier 50%. Lead-time buffers are 0% up to 21 days, 0.3% above 21 days, 0.75% above 30 days and 1.5% above 45 days. Incoterm freight exposure is DDP 0%, DAP 20% of maximum, CIF 35%, FOB 75%, EXW 100%, and unknown 60% of maximum. These are model assumptions, not universal market standards.",
        ("modules/tco.py::calculate_supplier_tco", "modules/tco.py::freight_factor_for_incoterm"),
    ),
    _entry(
        "supplier risk",
        ("risk", "supplier risk", "risk score", "failure probability", "risk methodology"),
        "Supplier risk is a deterministic repository calculation used by TCO, recommendation and supplier-intelligence paths. In TCO, failure probability is derived from the inverse of the risk score and capped by the configured maximum failure probability; the resulting penalty is multiplied by the configured business-impact factor. SourceMate explains the registered logic but does not recalculate a supplier score.",
        ("modules/risk.py", "modules/tco.py::calculate_supplier_tco", "modules/risk_intelligence.py"),
    ),
    _entry(
        "supplier scoring and performance",
        ("supplier score", "scoring", "performance score", "supplier performance", "weights", "score weighting"),
        "Supplier evaluation is deterministic and combines governed commercial, performance, risk, ESG and category evidence according to the applicable route. Recommendation eligibility is evaluated separately from ranking so that an ineligible supplier cannot become an award recommendation solely because of a high score.",
        ("modules/scoring.py", "modules/performance.py", "modules/recommendation_eligibility.py", "modules/supplier_recommendation_engine.py"),
    ),
    _entry(
        "supplier relationship management classification",
        ("srm", "srm rating", "srm criteria", "srm score", "srm classification", "relationship rating", "strategic supplier", "preferred supplier", "bifurcation"),
        "SRM means Supplier Relationship Management. The governed strategic index is structured as follows:\n\n| Particular | Weight |\n|---|---:|\n| Supplier performance | 25% |\n| Risk score | 20% |\n| Innovation | 15% |\n| ESG maturity | 10% |\n| Financial stability | 10% |\n| Business criticality | 10% |\n| Switching difficulty | 5% |\n| Supplier concentration | 5% |\n\nClassification rules:\n\n| Classification | Governed rule |\n|---|---|\n| Exit Candidate | Performance below 45, risk below 40, or financial stability below 35 |\n| Development | Performance below 60 or risk below 55 |\n| Strategic | Strategic index at least 80 and business criticality at least 70 |\n| Preferred | Strategic index at least 70 |\n| Approved | Strategic index at least 58 |\n| Transactional | Remaining suppliers below the Approved threshold |\n\nEach class has a defined governance cadence and relationship strategy. Human review remains mandatory.",
        ("modules/srm_engine.py::classify_supplier_relationship",),
    ),
    _entry(
        "financial ESG and innovation intelligence",
        ("financial", "financial health", "esg", "what esg stands for", "esg meaning", "environmental social governance", "sustainability", "innovation", "supplier intelligence"),
        "ESG stands for Environmental, Social and Governance.\n\n| Dimension | Procurement meaning in this project |\n|---|---|\n| Environmental | Carbon, recyclability, PCR content, EPR readiness and related sustainability indicators. |\n| Social | Supplier practices and continuity-related evidence represented by the available portfolio data; this is not an independent social audit. |\n| Governance | Certifications, controls, review evidence and governed supplier-management indicators. |\n\nSupplier 360 combines financial-stability indicators, ESG maturity, innovation evidence, performance and SRM classification. These are portfolio decision-support indicators based on supplied or synthetic evidence; they are not independent credit ratings, legal certifications or external ESG assurance.",
        ("modules/supplier_financial_engine.py", "modules/supplier_esg_intelligence.py", "modules/supplier_innovation_engine.py", "modules/supplier360_engine.py"),
    ),
    _entry(
        "supplier recommendations",
        ("recommendation", "recommend supplier", "award recommendation", "best supplier", "ranking"),
        "Recommendations are governed decision-support outputs built from deterministic eligibility, score, risk and category evidence. They remain recommendations for human review; SourceMate cannot approve, award or override qualification and eligibility controls.",
        ("modules/recommendation.py", "modules/recommendation_eligibility.py", "modules/supplier_recommendation_engine.py"),
    ),
    _entry(
        "multi-supplier allocation",
        ("allocation", "supplier allocation", "split award", "capacity", "minimum share", "maximum share"),
        "The governed multi-supplier allocation route applies explicit feasibility and share controls before presenting an allocation. Missing capacity or other required evidence can block the route. The portfolio does not execute an award or production allocation; it presents a reviewable decision-support result and failure evidence.",
        ("modules/multi_supplier_allocation.py", "modules/multi_supplier_allocation_feasibility.py", "modules/multi_supplier_allocation_route.py"),
    ),
    _entry(
        "scenario analysis",
        ("scenario", "stress test", "what if", "shock", "demand change", "freight shock", "raw material shock"),
        "Scenario analysis changes controlled inputs such as raw-material shock, freight shock, demand change, FX or category-specific stress assumptions and reruns the existing deterministic route. Scenario outputs are comparative decision support, not forecasts or external market predictions.",
        ("modules/scenario.py", "modules/scenario_engine.py", "modules/steel_scenario.py"),
    ),
    _entry(
        "RFQ processing",
        ("rfq", "request for quotation", "upload", "workbook", "normalization", "supplier quote"),
        "The RFQ layer ingests controlled CSV or Excel data, maps fields, validates structure, normalizes values and preserves review evidence before analytical handoff. It does not send RFQs, negotiate with suppliers or write approved outcomes to ERP.",
        ("modules/intelligent_rfq.py", "modules/rfq_workbook_adapter.py", "modules/rfq_normalization_bridge.py", "modules/rfq_integration_controller.py"),
    ),
    _entry(
        "assumptions and precedence",
        ("assumption", "default", "precedence", "override", "input source", "parameter source"),
        "Governed parameter precedence is RFQ override, then supplier-specific value, then category value, then global default. Candidate and rejected evidence are retained; conflicts, incompatible units and invalid effective dates fail closed instead of being silently resolved.",
        ("modules/parameter_precedence.py", "modules/assumption_provenance.py", "modules/parameter_profile_records.py"),
    ),
    _entry(
        "currency and unit governance",
        ("currency", "usd", "inr", "fx", "exchange rate", "unit", "conversion"),
        "Canonical calculations remain in USD unless the authoritative category service specifies otherwise. The Explorer USD, INR or Both selection is display-only and uses the stated USD-INR rate. Trace and reconciliation retain canonical values so display conversion cannot change calculation authority.",
        ("modules/currency_unit_governance.py", "modules/unit_display.py", "modules/calculation_explorer_currency_ui.py"),
    ),
    _entry(
        "exports evidence and reconciliation",
        ("export", "evidence", "trace", "reconciliation", "audit", "provenance", "excel", "json"),
        "Exports, trace and reconciliation provide repository evidence of how a result was produced and compared. Exact matches, tolerated differences, mismatches and unavailable evidence are separately classified. Internal evidence references demonstrate provenance but do not prove external supplier or market verification.",
        ("modules/export_evidence_registry.py", "modules/calculation_trace.py", "modules/calculation_reconciliation.py", "modules/evidence_assurance.py"),
    ),
    _entry(
        "governance limitations and deferred capabilities",
        ("governance", "limitation", "cannot", "web", "external", "production", "erp", "autonomous", "approval", "deferred"),
        "The portfolio is read-only, validation-gated and human-review mandatory. SourceMate does not browse the web, retrieve external evidence, ingest documents, run OCR, use RAG, execute formulas, approve suppliers, create awards, allocate production, write to ERP, sign contracts or claim realized savings. Production integration and autonomous authority are explicitly deferred.",
        ("PROJECT_CONTROL.md", "modules/sourcemate_conversation.py", "app.py"),
    ),
)


def _tokens(text: str) -> set[str]:
    normalized = "".join(ch.lower() if ch.isalnum() else " " for ch in str(text or ""))
    return {token for token in normalized.split() if len(token) > 1}


def search_project_knowledge(question: str) -> list[Mapping[str, Any]]:
    """Return the highest-scoring grounded project entries for a question."""
    question_text = str(question or "").strip().lower()
    question_tokens = _tokens(question_text)
    scored: list[tuple[int, Mapping[str, Any]]] = []
    for item in PROJECT_KNOWLEDGE:
        score = 0
        topic = str(item["topic"]).lower()
        if topic in question_text:
            score += 12
        for alias in item["aliases"]:
            alias_text = str(alias).lower()
            if alias_text in question_text:
                score += 8 + len(_tokens(alias_text))
        score += len(question_tokens & _tokens(topic)) * 2
        for alias in item["aliases"]:
            score += len(question_tokens & _tokens(alias))
        if score:
            scored.append((score, item))
    scored.sort(key=lambda pair: (-pair[0], str(pair[1]["topic"])))
    if not scored:
        return []
    best = scored[0][0]
    return [item for score, item in scored[:3] if score >= max(3, best - 3)]


def project_topic_catalogue() -> tuple[str, ...]:
    return tuple(str(item["topic"]) for item in PROJECT_KNOWLEDGE)
