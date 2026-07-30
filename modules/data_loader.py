"""Data loading and synthetic demo data."""

from __future__ import annotations

from zipfile import BadZipFile

import pandas as pd

from modules.intelligent_rfq import normalize_rfq_dataframe


class RFQUploadError(ValueError):
    """Business-facing upload failure that is safe to show in the Streamlit UI."""


def get_demo_suppliers():
    """Return synthetic RFQ data for the packaging procurement demo."""
    return pd.DataFrame([
        {"Supplier":"Apex Packaging Corp","Quoted Unit Price USD":0.42,"Currency":"USD","Unit":"piece","MOQ":10000,"Lead Time Days":14,"Payment Terms":"Net 30","Incoterms":"DDP","OTIF %":94,"Quality PPM":850,"Audit Score":82,"Complaint Rate %":1.5,"Capacity Buffer %":18,"Recyclability":90,"Certification":85,"Carbon Score":75,"EPR Readiness":80,"PCR Content %":20,"Risk Category":"Low"},
        {"Supplier":"Vertex Global Print","Quoted Unit Price USD":0.38,"Currency":"USD","Unit":"piece","MOQ":50000,"Lead Time Days":30,"Payment Terms":"Advance 50%","Incoterms":"FOB","OTIF %":87,"Quality PPM":1600,"Audit Score":72,"Complaint Rate %":3.8,"Capacity Buffer %":8,"Recyclability":82,"Certification":70,"Carbon Score":68,"EPR Readiness":65,"PCR Content %":10,"Risk Category":"Medium"},
        {"Supplier":"Matrix Logistics & Pack","Quoted Unit Price USD":0.45,"Currency":"USD","Unit":"piece","MOQ":5000,"Lead Time Days":7,"Payment Terms":"Net 60","Incoterms":"DDP","OTIF %":97,"Quality PPM":500,"Audit Score":88,"Complaint Rate %":0.8,"Capacity Buffer %":22,"Recyclability":92,"Certification":90,"Carbon Score":82,"EPR Readiness":88,"PCR Content %":25,"Risk Category":"Low"},
    ])


def get_kraft_paper_demo_suppliers():
    """Return three synthetic Kraft Paper supplier quotations in USD/kg."""
    return pd.DataFrame([
        {"Supplier":"Western Fibre Mills","Material":"Kraft Paper","Kraft Variant":"Recycled Kraft","GSM":150,"Strength Grade":"22 BF","Quoted Unit Price USD":0.84,"Currency":"USD","Unit":"kg","MOQ":25000,"Lead Time Days":14,"Payment Terms":"Net 45","Incoterms":"DDP","OTIF %":95,"Quality PPM":700,"Audit Score":87,"Complaint Rate %":1.1,"Capacity Buffer %":20,"Supplier Capacity":900000,"Commodity Volatility %":16,"Import Dependency %":5,"Supplier Concentration %":38,"Substitute Available":"Yes","Duty %":0,"Recyclability":96,"Certification":84,"Carbon Score":77,"EPR Readiness":82,"PCR Content %":92,"Mill Allocation %":70,"Moisture %":7.5,"Fibre Availability %":78,"Quality Continuity Score":86,"Corrugated Linkage":"Approved demonstration assumption"},
        {"Supplier":"National Kraft Industries","Material":"Kraft Paper","Kraft Variant":"Virgin Kraft","GSM":150,"Strength Grade":"22 BF","Quoted Unit Price USD":0.96,"Currency":"USD","Unit":"kg","MOQ":40000,"Lead Time Days":24,"Payment Terms":"Net 30","Incoterms":"CIF","OTIF %":91,"Quality PPM":520,"Audit Score":90,"Complaint Rate %":0.8,"Capacity Buffer %":14,"Supplier Capacity":1100000,"Commodity Volatility %":18,"Import Dependency %":22,"Supplier Concentration %":52,"Substitute Available":"Yes","Duty %":3,"Recyclability":92,"Certification":90,"Carbon Score":73,"EPR Readiness":78,"PCR Content %":0,"Mill Allocation %":82,"Moisture %":6.8,"Fibre Availability %":88,"Quality Continuity Score":92,"Corrugated Linkage":"Approved demonstration assumption"},
        {"Supplier":"Circular Paperworks Ltd","Material":"Kraft Paper","Kraft Variant":"Recycled Kraft","GSM":150,"Strength Grade":"22 BF","Quoted Unit Price USD":0.80,"Currency":"USD","Unit":"kg","MOQ":50000,"Lead Time Days":32,"Payment Terms":"Advance 20%","Incoterms":"FOB","OTIF %":86,"Quality PPM":1250,"Audit Score":76,"Complaint Rate %":2.7,"Capacity Buffer %":9,"Supplier Capacity":750000,"Commodity Volatility %":24,"Import Dependency %":10,"Supplier Concentration %":68,"Substitute Available":"No","Duty %":0,"Recyclability":98,"Certification":76,"Carbon Score":81,"EPR Readiness":80,"PCR Content %":95,"Mill Allocation %":92,"Moisture %":9.2,"Fibre Availability %":58,"Quality Continuity Score":68,"Corrugated Linkage":"Conditional demonstration assumption"},
    ])


def get_raw_material_demo_suppliers(commodity="PET Resin"):
    """Return coherent synthetic raw-material RFQ data in USD per category unit."""
    if commodity == "Kraft Paper":
        return get_kraft_paper_demo_suppliers()

    base_prices = {
        "PET Resin": 1.27,
        "Polyethylene": 1.34,
        "Polypropylene": 1.30,
        "Aluminium Foil": 3.18,
        "Steel": 1.04,
        "Copper": 9.65,
    }
    if commodity not in base_prices:
        raise ValueError(f"Unsupported synthetic raw-material commodity '{commodity}'.")

    base = base_prices[commodity]
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
    data.attrs["assumption_profile_version"] = "C1.0" if commodity == "Kraft Paper" else "S1"
    data.attrs["category"] = category
    data.attrs["commodity"] = commodity
    return data


def _read_uploaded_dataframe(uploaded_file):
    """Read one supported RFQ file and translate parser failures into actionable guidance."""
    filename = str(getattr(uploaded_file, "name", "") or "").strip()
    suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if suffix not in {"csv", "xlsx"}:
        raise RFQUploadError(
            "Unsupported RFQ file type. Upload a .csv or .xlsx file exported as a standard table."
        )
    try:
        return pd.read_csv(uploaded_file) if suffix == "csv" else pd.read_excel(uploaded_file)
    except pd.errors.EmptyDataError as exc:
        raise RFQUploadError(
            "The uploaded RFQ file is empty. Add a header row and at least one supplier quotation, then upload it again."
        ) from exc
    except pd.errors.ParserError as exc:
        raise RFQUploadError(
            "The CSV structure could not be parsed. Check delimiters, quotation marks and merged header rows, then export the file again."
        ) from exc
    except (BadZipFile, ImportError) as exc:
        raise RFQUploadError(
            "The Excel workbook could not be opened. Confirm that it is a valid .xlsx file and is not password-protected or corrupted."
        ) from exc
    except (OSError, ValueError) as exc:
        raise RFQUploadError(
            "The RFQ file could not be opened. Confirm that the file is not corrupted, password-protected or still open in another application."
        ) from exc


def load_uploaded_rfq(uploaded_file):
    """Load, recognize, and normalize an uploaded CSV or Excel RFQ file."""
    if uploaded_file is None:
        return None
    raw_df = _read_uploaded_dataframe(uploaded_file)
    if raw_df.empty:
        raise RFQUploadError(
            "The uploaded RFQ contains headers but no supplier rows. Add at least one supplier quotation and upload the file again."
        )
    try:
        normalized_df, report = normalize_rfq_dataframe(raw_df)
    except (KeyError, TypeError, ValueError) as exc:
        raise RFQUploadError(
            "The RFQ columns could not be mapped reliably. Use one header row, remove merged cells and include clear supplier, price, MOQ, lead-time, payment-term and Incoterm columns."
        ) from exc
    normalized_df.attrs["rfq_quality_report"] = report
    normalized_df.attrs["source_label"] = "Uploaded unverified supplier data"
    return normalized_df
