from modules.executive_outputs import generate_supplier_email


SUPPLIER = {"Supplier": "Bharat Advanced Polymers", "Quoted Unit Price USD": 1.321}


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
