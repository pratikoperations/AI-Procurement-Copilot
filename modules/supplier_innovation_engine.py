"""Supplier innovation maturity intelligence."""


def _clip(value):
    return round(max(0.0, min(100.0, float(value))), 1)


def evaluate_supplier_innovation(row, category="Packaging Procurement"):
    design = float(row.get("Design Capability Score", 60))
    packaging = float(row.get("Packaging Innovation Score", 65 if category == "Packaging Procurement" else 50))
    material = float(row.get("Material Innovation Score", 65))
    savings = float(row.get("Cost Reduction Ideas Score", 60))
    automation = float(row.get("Automation Score", 60))
    digital = float(row.get("Digital Maturity Score", 60))
    sharing = float(row.get("Data Sharing Score", 55))
    ai = float(row.get("AI Readiness Score", 45))
    improvement = float(row.get("Continuous Improvement Score", 65))
    sustainability = float(row.get("Sustainability Innovation Score", 60))
    prototype = float(row.get("Prototype Speed Score", 60))
    score = _clip((design + packaging + material + savings + automation + digital + sharing + ai + improvement + sustainability + prototype) / 11)
    level = "Leading" if score >= 85 else "Advanced" if score >= 75 else "Developing" if score >= 60 else "Basic" if score >= 45 else "Low"
    dimensions = {"Design":design,"Packaging":packaging,"Material":material,"Cost Reduction":savings,"Automation":automation,"Digital":digital,"Data Sharing":sharing,"AI Readiness":ai,"Continuous Improvement":improvement,"Sustainability":sustainability,"Prototype Speed":prototype}
    strengths = [k for k,v in dimensions.items() if v >= 75]
    gaps = [k for k,v in dimensions.items() if v < 55]
    opportunities = ["Joint value-engineering workshop", "Supplier-led cost-reduction pipeline", "Sustainability innovation roadmap", "Digital data-sharing pilot"]
    return {"innovation_score":score,"innovation_maturity_level":level,"innovation_strengths":strengths or ["No leading capability confirmed"],"innovation_gaps":gaps,"collaboration_opportunities":opportunities,"recommended_innovation_agenda":"Prioritize two measurable initiatives with value, owner, timeline, and implementation gate."}
