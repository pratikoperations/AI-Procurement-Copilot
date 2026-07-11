from modules.executive_outputs import generate_supplier_email
from modules.negotiation import generate_negotiation_playbook, govern_negotiation_brief


SUPPLIER = {
    "Supplier": "Bharat Advanced Polymers",
    "Quoted Unit Price USD": 1.321,
    "category_engine": "Raw Material Procurement",
    "Material": "PET Resin",
    "Unit": "kg",
}


def test_pet_resin_email_uses_kg_and_raw_material_terms():
    email = generate_supplier_email(SUPPLIER, 1.27, 500000, "Raw Material Procurement", "PET Resin", "kg", {"status":"Human Review Required","reason":"Review required","failed_checks":[]})
    lower = email.lower()
    assert "500,000 kg" in email
    assert "intrinsic viscosity" in lower
    assert "producer or conversion premium" in lower
    assert "printing" not in lower
    assert "tooling" not in lower


def test_packaging_email_may_use_packaging_terms():
    email = generate_supplier_email(SUPPLIER, 0.40, 500000, "Packaging Procurement", "Corrugated Board", "piece", {"status":"Eligible","reason":"Passed","failed_checks":[]})
    lower = email.lower()
    assert "printing" in lower
    assert "tooling" in lower
    assert "piece" in lower


def test_blocked_email_does_not_imply_selection():
    email = generate_supplier_email(SUPPLIER, 1.27, 500000, "Raw Material Procurement", "PET Resin", "kg", {"status":"Blocked","reason":"Mixed currency","failed_checks":["Mixed currency"]})
    lower = email.lower()
    assert "evaluation is paused" in lower
    assert "does not imply supplier selection" in lower
    assert "final award" not in lower


def test_raw_material_negotiation_uses_category_terms_and_kg():
    playbook = generate_negotiation_playbook(SUPPLIER, 1.27, "Indus Materials Ltd", 1.25, 10000)
    lower = playbook.lower()
    assert "per kg" in lower
    assert "commodity index" in lower
    assert "certificate of analysis" in lower
    assert "printing" not in lower
    assert "tooling" not in lower


def test_blocked_negotiation_brief_is_withheld():
    playbook = generate_negotiation_playbook(SUPPLIER, 1.27, "Indus Materials Ltd", 1.25, 10000)
    governed = govern_negotiation_brief(playbook, {"status":"Blocked", "reason":"Currency validation failed"})
    assert governed.startswith("NEGOTIATION BRIEF WITHHELD")
    assert "target and award-position language must not be used" in governed
