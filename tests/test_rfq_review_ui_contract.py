from modules import rfq_review_ui


def test_preview_label_preserves_global_release_boundary():
    assert "v1.3" in rfq_review_ui.PREVIEW_LABEL
    assert "Preview" in rfq_review_ui.PREVIEW_LABEL
    assert "not a v1.3 application release" in rfq_review_ui.PREVIEW_CAPTION


def test_preview_caption_preserves_claim_safety():
    caption = rfq_review_ui.PREVIEW_CAPTION.lower()
    assert "autonomous award" in caption
    assert "live erp" in caption
    assert "production deployment" in caption
