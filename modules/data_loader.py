"""Data loading and synthetic demo data for Build 0.2."""

import pandas as pd


def get_demo_suppliers():
    """Return starter synthetic RFQ data for the packaging procurement demo."""
    return pd.DataFrame(
        [
            {
                "Supplier": "Apex Packaging Corp",
                "Quoted Unit Price USD": 0.42,
                "MOQ": 10000,
                "Lead Time Days": 14,
                "Payment Terms": "Net 30",
                "Incoterms": "DDP",
                "OTIF %": 94,
                "Quality PPM": 850,
                "Risk Category": "Low",
            },
            {
                "Supplier": "Vertex Global Print",
                "Quoted Unit Price USD": 0.38,
                "MOQ": 50000,
                "Lead Time Days": 30,
                "Payment Terms": "Advance 50%",
                "Incoterms": "FOB",
                "OTIF %": 87,
                "Quality PPM": 1600,
                "Risk Category": "Medium",
            },
            {
                "Supplier": "Matrix Logistics & Pack",
                "Quoted Unit Price USD": 0.45,
                "MOQ": 5000,
                "Lead Time Days": 7,
                "Payment Terms": "Net 60",
                "Incoterms": "DDP",
                "OTIF %": 97,
                "Quality PPM": 500,
                "Risk Category": "Low",
            },
        ]
    )


def load_uploaded_rfq(uploaded_file):
    """Load uploaded CSV or Excel RFQ file."""
    if uploaded_file is None:
        return None
    if uploaded_file.name.lower().endswith(".csv"):
        return pd.read_csv(uploaded_file)
    return pd.read_excel(uploaded_file)
