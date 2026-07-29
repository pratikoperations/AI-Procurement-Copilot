from datetime import date

from modules.rfq_review_state import (
    ReviewIdentity,
    ReviewState,
    WarningDisposition,
    classify_orchestration_state,
    stable_digest,
    warning_controls,
    warning_disposition,
)


def test_build_d_outcomes_are_separate():
    assert classify_orchestration_state("BLOCKED") is ReviewState.ORCHESTRATION_BLOCKED
    assert classify_orchestration_state("INSUFFICIENT_EVIDENCE") is ReviewState.INSUFFICIENT_EVIDENCE
    assert classify_orchestration_state("ELIGIBLE_WITH_CONDITIONS") is ReviewState.CONDITIONAL_REVIEW_REQUIRED
    assert classify_orchestration_state("ELIGIBLE_FOR_ANALYSIS") is ReviewState.ANALYTICAL_REVIEW_READY


def test_unknown_warning_fails_closed():
    assert warning_disposition("FUTURE_UNKNOWN", "QUICK_RFQ") is WarningDisposition.COMPATIBILITY_BLOCKING


def test_warning_controls_require_acknowledgement():
    blocking, outstanding = warning_controls(["HISTORY_STALE"], "QUICK_RFQ")
    assert not blocking
    assert outstanding == ("HISTORY_STALE",)
    blocking, outstanding = warning_controls(["HISTORY_STALE"], "QUICK_RFQ", ["HISTORY_STALE"])
    assert not blocking and not outstanding


def test_zero_price_is_compatibility_blocking():
    blocking, outstanding = warning_controls(["ZERO_PRICE_REQUIRES_CLASSIFICATION"], "QUICK_RFQ")
    assert blocking == ("ZERO_PRICE_REQUIRES_CLASSIFICATION",)
    assert not outstanding


def test_review_identity_changes_with_display_mode():
    base = dict(
        upload_hash_sha256="a" * 64,
        schema_version="1.3.0",
        alias_registry_version="1.3.0",
        selected_sourcing_event_id="E1",
        selected_rfq_number="R1",
        selected_rfq_item="10",
        canonical_engine_currency="USD",
        evaluation_date=date(2026, 7, 29),
        evaluation_date_source="EXPLICIT_INPUT",
        adapter_finding_digest=stable_digest([]),
        orchestration_finding_digest=stable_digest([]),
        compatibility_manifest_digest=stable_digest([]),
        approved_mapping_digest=stable_digest([]),
        approved_history_mapping_digest=stable_digest([]),
        manual_history_confirmation_digest=stable_digest([]),
    )
    usd = ReviewIdentity(display_currency_mode="USD", **base)
    both = ReviewIdentity(display_currency_mode="BOTH", **base)
    assert usd.digest != both.digest
