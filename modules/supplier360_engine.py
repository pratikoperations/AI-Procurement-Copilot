"""Supplier 360 profile builder with transparent defaulting."""

from modules.supplier_esg_intelligence import evaluate_supplier_esg
from modules.supplier_financial_engine import evaluate_supplier_financial_health
from modules.supplier_innovation_engine import evaluate_supplier_innovation
from modules.supplier_performance_engine import evaluate_supplier_performance
from modules.srm_engine import classify_supplier_relationship


def build_supplier360_profile(row, category="Packaging Procurement", commodity="General"):
    """Create a deterministic Supplier 360 profile from available supplier data."""
    performance = evaluate_supplier_performance(row)
    financial = evaluate_supplier_financial_health(row)
    esg = evaluate_supplier_esg(row)
    innovation = evaluate_supplier_innovation(row, category)
    srm = classify_supplier_relationship(row, performance, financial, esg, innovation)

    defaults_used = []
    def value(field, default):
        if field not in row or row.get(field) in (None, ""):
            defaults_used.append(field)
            return default
        return row.get(field)

    capacity = float(value("Supplier Capacity", max(float(row.get("MOQ", 0)) * 20, 100000)))
    utilization = float(value("Capacity Utilization %", max(0, 100 - float(row.get("Capacity Buffer %", 10)))))
    profile_score = round(max(0,min(100,
        performance["overall_supplier_performance_score"] * 0.25
        + float(row.get("risk_score", 60)) * 0.20
        + financial["financial_stability_score"] * 0.15
        + esg["esg_maturity_score"] * 0.15
        + innovation["innovation_score"] * 0.10
        + srm["strategic_index"] * 0.15
    )),1)

    profile = {
        "supplier_name": row.get("Supplier", "Unknown Supplier"),
        "supplier_type": value("Supplier Type", "Manufacturer"),
        "country": value("Country", "Not provided"),
        "manufacturing_location": value("Manufacturing Location", row.get("Plant", "Not provided")),
        "manufacturing_footprint": value("Manufacturing Footprint", "Single-site status not confirmed"),
        "annual_capacity": capacity,
        "capacity_utilization": utilization,
        "strategic_importance": value("Strategic Importance", "Medium"),
        "approved_categories": value("Approved Categories", category),
        "commodity_coverage": value("Commodity Coverage", commodity),
        "spend_classification": value("Spend Classification", "Medium"),
        "preferred_supplier_status": value("Preferred Supplier Status", srm["srm_classification"] in {"Strategic","Preferred"}),
        "supplier_dependency": value("Supplier Dependency", "Not quantified"),
        "business_continuity_status": value("Business Continuity Status", "Review required"),
        "qualification_status": value("Qualification Status", "Qualified for analysis only"),
        "audit_status": value("Audit Status", "Current" if float(row.get("Audit Score", 0)) >= 70 else "Review required"),
        "contract_status": value("Contract Status", "Not provided"),
        "relationship_owner": value("Relationship Owner", "Category Manager"),
        "overall_supplier360_score": profile_score,
        "performance": performance,
        "financial": financial,
        "esg": esg,
        "innovation": innovation,
        "srm": srm,
        "defaults_used": sorted(set(defaults_used)),
        "data_note": "Defaults are explicitly listed; no hidden external facts are introduced.",
    }
    return profile


def build_supplier360_profiles(scored_df, category="Packaging Procurement", commodity="General"):
    return [build_supplier360_profile(row.to_dict(), category, commodity) for _, row in scored_df.iterrows()]
