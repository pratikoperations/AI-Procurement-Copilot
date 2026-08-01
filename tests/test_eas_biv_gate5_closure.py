"""Contract tests for EAS-BIV Gate 5 documentation and evidence closure."""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
CLOSURE = ROOT / "docs" / "EAS_BIV_FINAL_CLOSURE.md"
INTERVIEW_PACK = ROOT / "docs" / "EAS_BIV_INTERVIEW_EVIDENCE_PACK.md"
TEST_EVIDENCE = ROOT / "docs" / "06_TEST_EVIDENCE.md"
GOVERNANCE = ROOT / "docs" / "07_GOVERNANCE_AND_LIMITATIONS.md"
DEMO_GUIDE = ROOT / "docs" / "08_DEMO_GUIDE.md"

AUTHORITATIVE_SHA = "834b34db145cc0156196579f7419e7db7b438106"
ADAPTER_IDS = {
    "REC-PET",
    "REC-KRF",
    "REC-COR",
    "REC-LAM",
    "REC-STL",
    "REC-SCORE-GEN",
    "REC-ELG",
}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_gate5_closure_documents_exist():
    for path in (README, CLOSURE, INTERVIEW_PACK, TEST_EVIDENCE, GOVERNANCE, DEMO_GUIDE):
        assert path.is_file(), path


def test_authoritative_sha_and_ci_evidence_are_consistent():
    for path in (README, CLOSURE, INTERVIEW_PACK, TEST_EVIDENCE, GOVERNANCE):
        content = _text(path)
        assert AUTHORITATIVE_SHA in content, path
        assert "816" in content, path
        assert "1011" in content, path
    combined = "\n".join(_text(path) for path in (README, CLOSURE, INTERVIEW_PACK, TEST_EVIDENCE))
    assert "30706340753" in combined
    assert "91386012618" in combined
    assert "Python 3.11.15" in combined or "Python: `3.11.15`" in combined


def test_contract_versions_are_recorded():
    combined = "\n".join(_text(path) for path in (README, CLOSURE, INTERVIEW_PACK, TEST_EVIDENCE))
    assert "AIPC-GOVERNED-EXPLORER-1.0" in combined
    assert "AIPC-SOURCEMATE-BASIC-1.0" in combined
    assert "AIPC-CALC-TRACE-1.0" in combined


def test_adapter_coverage_and_deferred_boundary_are_disclosed():
    for path in (README, CLOSURE, INTERVIEW_PACK, GOVERNANCE):
        content = _text(path)
        found = {adapter_id for adapter_id in ADAPTER_IDS if f"`{adapter_id}`" in content}
        assert found == ADAPTER_IDS, (path, found)
        assert "unsupported_deferred_coverage" in content


def test_external_verification_and_autonomous_award_are_not_claimed():
    combined = "\n".join(_text(path).lower() for path in (README, CLOSURE, INTERVIEW_PACK, GOVERNANCE))
    assert "does not perform external verification" in combined
    assert "does not prove" in combined or "not prove" in combined
    assert "no autonomous award" in combined
    assert "human procurement approval remains mandatory" in combined or "human approval remains mandatory" in combined


def test_manual_hosted_and_mobile_validation_is_not_overstated():
    closure = _text(CLOSURE).lower()
    matrix_rows = [line for line in closure.splitlines() if line.startswith("|")]
    for observation in (
        "desktop hosted load",
        "narrow desktop viewport",
        "android portrait",
        "android landscape",
        "explorer navigation",
        "overview section",
        "assumptions section",
        "calculation trace section",
        "reconciliation section",
        "sourcemate section",
        "human review section",
        "packaging tco deferred state",
    ):
        row = next(line for line in matrix_rows if observation in line)
        assert "not performed" in row
    assert "physical browser and device observations are not inferred" in closure


def test_readme_links_to_gate5_closure_documents():
    readme = _text(README)
    assert "docs/EAS_BIV_FINAL_CLOSURE.md" in readme
    assert "docs/EAS_BIV_INTERVIEW_EVIDENCE_PACK.md" in readme


def test_gate5_closure_preserves_non_production_position():
    closure = _text(CLOSURE).lower()
    governance = _text(GOVERNANCE).lower()
    assert "does not modify production application functionality" in closure
    assert "formula metadata is documentation only" in governance
    assert "unavailable" in governance and "not inferred or reconstructed" in governance
    assert "no approval persistence" in governance
    assert "no autonomous supplier award" in governance
