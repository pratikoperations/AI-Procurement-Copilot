"""Data loading and synthetic demo data."""

import pandas as pd

from modules.intelligent_rfq import normalize_rfq_dataframe


def get_demo_suppliers():
    """Return synthetic RFQ data for the packaging procurement demo."""
    return pd.DataFrame([
        {"Supplier":"Apex Packaging Corp","Quoted Unit Price USD":0.42,"Currency":"USD","Unit":"piece","MOQ":10000,"Lead Time Days":14,"Payment Terms":"Net 30","Incoterms":"DDP","OTIF %":94,"Quality PPM":850,"Audit Score":82,"Complaint Rate %":1.5,"Capacity Buffer %":18,"Recyclability":90,"Certification":85,"Carbon Score":75,"EPR Readiness":80,"PCR Content %":20,"Risk Category":"Low"},
        {"Supplier":"Vertex Global Print","Quoted Unit Price USD":0.38,"Currency":"USD","Unit":"piece","MOQ":50000,"Lead Time Days":30,"Payment Terms":"Advance 50%","Incoterms":"FOB","OTIF %":87,"Quality PPM":1600,"Audit Score":72,"Complaint Rate %":3.8,"Capacity Buffer %":8,"Recyclability":82,"Certification":70,"Carbon Score":68,"EPR Readiness":65,"PCR Content %":10,"Risk Category":"Medium"},
        {"Supplier":"Matrix Logistics & Pack","Quoted Unit Price USD":0.45,"Currency":"USD","Unit":"piece","MOQ":5000,"Lead Time Days":7,"Payment Terms":"Net 60","Incoterms":"DDP","OTIF %":97,"Quality PPM":500,"Audit Score":88,"Complaint Rate %":0.8,"Capacity Buffer %":22,"Recyclability":92,"Certification":90,"Carbon Score":82,"EPR Readiness":88,"PCR Content %":25,"Risk Category":"Low"},
    ])


def get_raw_material_demo_suppliers(commodity="PET Resin"):
    """Return coherent synthetic raw-material RFQ data in USD per category unit."""
    base_prices = {"PET Resin":1.27,"Polyethylene":1.34,"Polypropylene":1.30,"Aluminium Foil":3.18,"Steel":1.04,"Copper":9.65}
    base = base_prices.get(commodity, 1.27)
    unit = "kg"
    return pd.DataFrame([
        {"Supplier":"Indus Materials Ltd","Material":commodity,"Quoted Unit Price USD":round(base,3),"Currency":"USD","Unit":unit,"MOQ":20000,"Lead Time Days":21,"Payment Terms":"Net 45","Incoterms":"CIF","OTIF %":95,"Quality PPM":650,"Audit Score":86,"Complaint Rate %":1.0,"Capacity Buffer %":20,"Supplier Capacity":800000,"Commodity Volatility %":14,"Import Dependency %":45,"Supplier Concentration %":40,"Substitute Available":"Yes","Duty %":5,"Recyclability":75,"Certification":85,"Carbon Score":72,"EPR Readiness":70,"PCR Content %":15},
        {"Supplier":"Global Commodity Corp","Material":commodity,"Quoted Unit Price USD":round(base*0.96,3),"Currency":"USD","Unit":unit,"MOQ":50000,"Lead Time Days":45,"Payment Terms":"Advance 20%","Incoterms":"FOB","OTIF %":88,"Quality PPM":1200,"Audit Score":76,"Complaint Rate %":2.8,"Capacity Buffer %":8,"Supplier Capacity":1200000,"Commodity Volatility %":28,"Import Dependency %":85,"Supplier Concentration %":70,"Substitute Available":"No","Duty %":8,"Recyclability":70,"Certification":75,"Carbon Score":65,"EPR Readiness":62,"PCR Content %":10},
        {"Supplier":"Bharat Advanced Polymers","Material":commodity,"Quoted Unit Price USD":round(base*1.04,3),"Currency":"USD","Unit":unit,"MOQ":10000,"Lead Time Days":12,"Payment Terms":"Net 60","Incoterms":"DDP","OTIF %":97,"Quality PPM":450,"Audit Score":91,"Complaint Rate %":0.6,"Capacity Buffer %":25,"Supplier Capacity":650000,"Commodity Volatility %":12,"Import Dependency %":20,"Supplier Concentration %":30,"Substitute Available":"Yes","Duty %":0,"Recyclability":80,"Certification":90,"Carbon Score":78,"EPR Readiness":76,"PCR Content %":18},
    ])


def get_demo_data(category="Packaging Procurement", commodity="Corrugated Board"):
    """Return category-appropriate synthetic data with explicit currency and unit."""
    data = get_raw_material_demo_suppliers(commodity) if category == "Raw Material Procurement" else get_demo_suppliers()
    data.attrs["source_label"] = "Synthetic demonstration data"
    return data


def load_uploaded_rfq(uploaded_file):
    """Load, recognize, and normalize an uploaded CSV or Excel RFQ file."""
    if uploaded_file is None:
        return None
    raw_df = pd.read_csv(uploaded_file) if uploaded_file.name.lower().endswith(".csv") else pd.read_excel(uploaded_file)
    normalized_df, report = normalize_rfq_dataframe(raw_df)
    normalized_df.attrs["rfq_quality_report"] = report
    normalized_df.attrs["source_label"] = "Uploaded unverified supplier data"
    return normalized_df
