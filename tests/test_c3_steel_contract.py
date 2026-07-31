"""Contract-only tests for the frozen C3 Steel planning phase."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs" / "C3_STEEL_CONTRACT.md"
LEDGER = ROOT / "docs" / "C3_ACTIVITY_DECISION_LEDGER.md"

PROFILES = (
    "CR_COIL_COMMERCIAL",
    "GI_COIL_Z120",
    "PPGI_COIL_Z120",
)

SCENARIOS = (
    "Base Case",
    "Steel Index +20%",
    "Energy and Conversion Premium +15%",
    "Import Duty and FX Stress",
    "Demand +25%",
    "Mill Allocation and Capacity Stress",
    "Grade-Substitution Scenario",
)

EXCEL_SHEETS = (
    "Supplier Scores Report",
    "Supplier Comparison",
    "Should Cost",
    "Allocation",
    "Standard Allocation",
    "Optimized Allocation",
    "Scenarios",
    "Audit Supplier Scores",
    "C3 Governance",
)


def _text(path: Path) -> str:
    assert path.exists(), f"Missing governed C3.0 document: {path}"
    return path.read_text(encoding="utf-8")


def test_c3_contract_documents_exist():
    assert CONTRACT.is_file()
    assert LEDGER.is_file()


def test_exact_three_controlled_profiles_and_attributes_are_frozen():
    contract = _text(CONTRACT)
    for profile in PROFILES:
        assert contract.count(f"`{profile}`") == 1

    assert "0.80 mm" in contract
    assert "0.60 mm" in contract
    assert "0.50 mm" in contract
    assert "1,000–1,250 mm" in contract
    assert "120 g/m² total" in contract
    assert "Topcoat 20 μm; back coat 5 μm" in contract


def test_commercial_and_currency_contract_is_explicit():
    contract = _text(CONTRACT)
    required = (
        "Annual-volume input: kg",
        "Optional reporting conversion: metric tonnes",
        "Internal governed calculation currency: USD",
        "Normalized comparison basis: USD/kg",
        "`USD`, `INR`, `Both`",
        "Accepted supplier quotation currencies: `USD`, `INR`",
        "single USD calculation path",
        "separate numeric USD and INR columns",
        "not live market data",
    )
    for phrase in required:
        assert phrase in contract


def test_currency_fail_closed_and_decision_invariance_are_frozen():
    contract = _text(CONTRACT)
    for phrase in (
        "missing FX rate",
        "non-numeric FX rate",
        "zero FX rate",
        "negative FX rate",
        "unsupported quote currency",
        "eligibility, supplier ranking, winner, allocation, scenario status, confidence or risk outcome",
    ):
        assert phrase in contract


def test_should_cost_component_contract_is_complete():
    contract = _text(CONTRACT)
    for component in (
        "base steel",
        "profile or grade premium",
        "rolling/conversion premium",
        "zinc coating where applicable",
        "paint or surface treatment where applicable",
        "energy surcharge",
        "yield-loss effect",
        "slitting/cutting",
        "packing",
        "freight",
        "duty",
        "supplier margin",
    ):
        assert component in contract


def test_fail_closed_eligibility_definitions_are_complete():
    contract = _text(CONTRACT)
    for control in (
        "exact selected profile",
        "controlled grade family",
        "thickness capability",
        "width capability",
        "zinc coating capability",
        "paint-line capability",
        "surface requirement",
        "mill or supplier approval",
        "application approval",
        "test-certificate availability",
        "supplier capacity",
        "coil-weight compatibility",
        "substitution approval",
    ):
        assert control in contract
    assert "technically ineligible supplier cannot become the governed winner because of price" in contract


def test_exact_seven_scenarios_are_frozen():
    contract = _text(CONTRACT)
    scenario_section = contract.split("## Governed scenarios", 1)[1].split("## Intended export contract", 1)[0]
    numbered_lines = [line for line in scenario_section.splitlines() if line[:1].isdigit()]
    assert len(numbered_lines) == 7
    for scenario in SCENARIOS:
        assert scenario_section.count(scenario) == 1


def test_export_contract_is_frozen():
    contract = _text(CONTRACT)
    for sheet in EXCEL_SHEETS:
        assert sheet in contract
    assert "`steel_governance`" in contract
    assert "`allow_nan=False`" in contract
    assert "Non-finite values normalize to `null`" in contract
    assert "USD and INR values remain separate numeric fields" in contract


def test_claim_boundaries_are_explicit():
    contract = _text(CONTRACT)
    for boundary in (
        "metallurgical certification",
        "engineering substitution approval",
        "mill-test-certificate authentication",
        "production-readiness assurance",
        "live commodity or FX data",
        "realized-savings evidence",
        "autonomous supplier approval or award",
        "ERP write-back",
    ):
        assert boundary in contract


def test_c1_and_c2_governance_records_remain_present():
    assert (ROOT / "docs" / "C1_KRAFT_PAPER_CLOSURE.md").is_file()
    assert (ROOT / "docs" / "C2_FLEXIBLE_LAMINATES_CLOSURE.md").is_file()


def test_c3_phase_does_not_include_executable_steel_modules():
    assert not (ROOT / "modules" / "steel_cost.py").exists()
    assert not (ROOT / "modules" / "steel_validation.py").exists()
    assert not (ROOT / "modules" / "steel_risk.py").exists()


def test_ledger_records_documentation_only_scope():
    ledger = _text(LEDGER)
    assert "C3.0 contract documentation and contract tests only" in ledger
    assert "None of those executable features is authorized in C3.0" in ledger
    assert "S1, C1 and C2 remain preserved" in ledger
