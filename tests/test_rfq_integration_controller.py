from types import SimpleNamespace

from modules import rfq_integration_controller as controller
from modules.rfq_review_state import ReviewState


def test_route_flag_is_disabled_by_default():
    enabled, warning = controller.governed_route_enabled({})
    assert not enabled
    assert warning is None


def test_malformed_route_flag_fails_closed():
    enabled, warning = controller.governed_route_enabled({controller.ROUTE_FLAG: "maybe"})
    assert not enabled
    assert controller.ROUTE_FLAG in warning


def test_no_file_returns_no_dataframe():
    result = controller.run_governed_review(None, env={controller.ROUTE_FLAG: "true"})
    assert result.review_state is ReviewState.NO_FILE
    assert result.dataframe is None
    assert not result.analysis_handoff_allowed


def test_adapter_fatal_cannot_fall_through(monkeypatch):
    fake = SimpleNamespace(
        findings=(SimpleNamespace(severity="Fatal", code="X"),),
        mapping_reviews=(),
        available_sourcing_event_ids=(),
    )
    monkeypatch.setattr(controller, "adapt_v13_workbook", lambda *args, **kwargs: fake)
    result = controller.run_governed_review(b"workbook", filename="x.xlsx", env={controller.ROUTE_FLAG: "true"})
    assert result.review_state is ReviewState.ADAPTER_FATAL
    assert result.dataframe is None


def test_insufficient_evidence_never_reaches_compatibility(monkeypatch):
    adapter = SimpleNamespace(
        findings=(),
        mapping_reviews=(),
        available_sourcing_event_ids=("E1",),
        selected_sourcing_event_id="E1",
        mode="QUICK_RFQ",
    )
    orchestration = SimpleNamespace(
        eligibility_status="INSUFFICIENT_EVIDENCE",
        conditional_findings=(),
    )
    monkeypatch.setattr(controller, "adapt_v13_workbook", lambda *args, **kwargs: adapter)
    monkeypatch.setattr(controller, "orchestrate_adapter_result", lambda *args, **kwargs: orchestration)
    called = {"compatibility": False}

    def compatibility(*args, **kwargs):
        called["compatibility"] = True
        raise AssertionError("Compatibility must not run")

    monkeypatch.setattr(controller, "assess_legacy_compatibility", compatibility)
    result = controller.run_governed_review(
        b"workbook",
        filename="x.xlsx",
        selected_sourcing_event_id="E1",
        env={controller.ROUTE_FLAG: "true"},
    )
    assert result.review_state is ReviewState.INSUFFICIENT_EVIDENCE
    assert result.dataframe is None
    assert not called["compatibility"]


def test_multiple_events_require_explicit_selection(monkeypatch):
    adapter = SimpleNamespace(
        findings=(),
        mapping_reviews=(),
        available_sourcing_event_ids=("E1", "E2"),
    )
    monkeypatch.setattr(controller, "adapt_v13_workbook", lambda *args, **kwargs: adapter)
    result = controller.run_governed_review(b"workbook", filename="x.xlsx", env={controller.ROUTE_FLAG: "true"})
    assert result.review_state is ReviewState.EVENT_SELECTION_REQUIRED
    assert result.dataframe is None
