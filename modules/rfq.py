"""RFQ processing placeholders for Build 0.2."""

REQUIRED_RFQ_COLUMNS = [
    "Supplier",
    "Quoted Unit Price USD",
    "MOQ",
    "Lead Time Days",
    "Payment Terms",
    "Incoterms",
]


def validate_rfq_columns(df):
    """Return missing required RFQ columns."""
    return [col for col in REQUIRED_RFQ_COLUMNS if col not in df.columns]
