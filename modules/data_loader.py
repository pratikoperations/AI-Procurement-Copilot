"""Data loading and synthetic demo data."""

from __future__ import annotations

from zipfile import BadZipFile
import pandas as pd

from modules.flexible_laminate_cost import SUPPORTED_STRUCTURES
from modules.intelligent_rfq import normalize_rfq_dataframe
from modules.synthetic_supplier_expansion import (
    expand_flexible_laminates,
    expand_general_packaging,
    expand_kraft_paper,
    expand_steel,
)


class RFQUploadError(ValueError):
    """Business-facing upload failure that is safe to show in the Streamlit UI."""


def _expanded_pool_enabled(expanded_supplier_pool: bool | None) -> bool:
    """Resolve an explicit selector, otherwise enable expansion only in Streamlit runtime."""
    if expanded_supplier_pool is not None:
        return bool(expanded_supplier_pool)
    try:
        import streamlit as st
        return bool(st.runtime.exists())
    except Exception:
        return False


def get_demo_suppliers():
    return pd.DataFrame([
        {"Supplier":"Apex Packaging Corp","Quoted Unit Price USD":0.42,"Currency":"USD","Unit":"piece","MOQ":10000,"Lead Time Days":14,"Payment Terms":"Net 30","Incoterms":"DDP","OTIF %":94,"Quality PPM":850,"Audit Score":82,"Complaint Rate %":1.5,"Capacity Buffer %":18,"Recyclability":90,"Certification":85,"Carbon Score":75,"EPR Readiness":80,"PCR Content %":20,"Risk Category":"Low"},
        {"Supplier":"Vertex Global Print","Quoted Unit Price USD":0.38,"Currency":"USD","Unit":"piece","MOQ":50000,"Lead Time Days":30,"Payment Terms":"Advance 50%","Incoterms":"FOB","OTIF %":87,"Quality PPM":1600,"Audit Score":72,"Complaint Rate %":3.8,"Capacity Buffer %":8,"Recyclability":82,"Certification":70,"Carbon Score":68,"EPR Readiness":65,"PCR Content %":10,"Risk Category":"Medium"},
        {"Supplier":"Matrix Logistics & Pack","Quoted Unit Price USD":0.45,"Currency":"USD","Unit":"piece","MOQ":5000,"Lead Time Days":7,"Payment Terms":"Net 60","Incoterms":"DDP","OTIF %":97,"Quality PPM":500,"Audit Score":88,"Complaint Rate %":0.8,"Capacity Buffer %":22,"Recyclability":92,"Certification":90,"Carbon Score":82,"EPR Readiness":88,"PCR Content %":25,"Risk Category":"Low"},
    ])


def get_flexible_laminate_demo_suppliers(structure: str):
    """Return three deterministic quotations with synthetic C2 risk assumptions."""
    if structure not in SUPPORTED_STRUCTURES:
        raise ValueError(f"Unsupported Flexible Laminates structure '{structure}'.")
    profile = SUPPORTED_STRUCTURES[structure]
    micron = {"PET / PE":70,"PET / MetPET / PE":85,"BOPP / CPP":60}[structure]
    base_price = {"PET / PE":2.05,"PET / MetPET / PE":2.38,"BOPP / CPP":1.92}[structure]
    common = {
        "Material":"Flexible Laminates","Laminate Structure":structure,"Layer Count":profile["layer_count"],
        "Currency":"USD","Unit":"kg","Total Micron":micron,"Print Profile":"Up to 4 colours",
        "Print Process":"Rotogravure","Number of Colours":4,"Adhesive Type":"Solvent-free",
        "Printing Loss %":3.0,"Lamination Loss %":2.0,"Slitting Loss %":1.0,"Tooling Status":"New",
        "Existing Tooling Available":"Not applicable","Tooling Availability":"Not applicable",
        "Tooling Cost per Colour USD":250.0,"Tooling Lifetime Volume kg":250000,
        "Application Approval Status":"Approved",
    }
    rows = [
        {**common,"Supplier":"Precision Flexibles Ltd","Quoted Unit Price USD":round(base_price,3),"MOQ":12000,"Lead Time Days":18,"Payment Terms":"Net 45","Incoterms":"DDP","OTIF %":95,"Quality PPM":650,"Audit Score":88,"Complaint Rate %":1.0,"Capacity Buffer %":18,"Supplier Capacity":900000,"Recyclability":62,"Certification":88,"Carbon Score":74,"EPR Readiness":72,"PCR Content %":0,"Substrate Availability %":82,"Press Capacity Utilisation %":76,"Lamination Capacity Utilisation %":78,"Printing Capability Score":88,"Lamination Capability Score":86,"Bond Strength Continuity Score":84,"Seal Integrity Continuity Score":82,"Solvent Retention Control Score":86},
        {**common,"Supplier":"BarrierPack Films","Quoted Unit Price USD":round(base_price*1.06,3),"MOQ":20000,"Lead Time Days":24,"Payment Terms":"Net 30","Incoterms":"CIF","OTIF %":93,"Quality PPM":480,"Audit Score":91,"Complaint Rate %":0.7,"Capacity Buffer %":14,"Supplier Capacity":1100000,"Recyclability":48,"Certification":92,"Carbon Score":70,"EPR Readiness":68,"PCR Content %":0,"Substrate Availability %":90,"Press Capacity Utilisation %":81,"Lamination Capacity Utilisation %":80,"Printing Capability Score":92,"Lamination Capability Score":94,"Bond Strength Continuity Score":92,"Seal Integrity Continuity Score":90,"Solvent Retention Control Score":91},
        {**common,"Supplier":"Circular Laminate Solutions","Quoted Unit Price USD":round(base_price*0.94,3),"MOQ":30000,"Lead Time Days":32,"Payment Terms":"Advance 20%","Incoterms":"FOB","OTIF %":86,"Quality PPM":1350,"Audit Score":76,"Complaint Rate %":2.8,"Capacity Buffer %":8,"Supplier Capacity":700000,"Recyclability":72,"Certification":76,"Carbon Score":80,"EPR Readiness":78,"PCR Content %":0,"Printing Loss %":5.5,"Lamination Loss %":4.0,"Slitting Loss %":2.0,"Substrate Availability %":58,"Press Capacity Utilisation %":92,"Lamination Capacity Utilisation %":93,"Printing Capability Score":74,"Lamination Capability Score":72,"Bond Strength Continuity Score":66,"Seal Integrity Continuity Score":64,"Solvent Retention Control Score":67},
    ]
    data = pd.DataFrame(rows)
    data.attrs["selected_laminate_structure"] = structure
    data.attrs["risk_assumption_basis"] = "Synthetic C2 capability and continuity assumptions; not audited supplier evidence."
    return data


def get_kraft_paper_demo_suppliers():
    return pd.DataFrame([
        {"Supplier":"Western Fibre Mills","Material":"Kraft Paper","Kraft Variant":"Recycled Kraft","GSM":150,"Strength Grade":"22 BF","Quoted Unit Price USD":0.84,"Currency":"USD","Unit":"kg","MOQ":25000,"Lead Time Days":14,"Payment Terms":"Net 45","Incoterms":"DDP","OTIF %":95,"Quality PPM":700,"Audit Score":87,"Complaint Rate %":1.1,"Capacity Buffer %":20,"Supplier Capacity":900000,"Commodity Volatility %":16,"Import Dependency %":5,"Supplier Concentration %":38,"Substitute Available":"Yes","Duty %":0,"Recyclability":96,"Certification":84,"Carbon Score":77,"EPR Readiness":82,"PCR Content %":92,"Mill Allocation %":70,"Moisture %":7.5,"Fibre Availability %":78,"Quality Continuity Score":86,"Corrugated Linkage":"Approved demonstration assumption"},
        {"Supplier":"National Kraft Industries","Material":"Kraft Paper","Kraft Variant":"Virgin Kraft","GSM":150,"Strength Grade":"22 BF","Quoted Unit Price USD":0.96,"Currency":"USD","Unit":"kg","MOQ":40000,"Lead Time Days":24,"Payment Terms":"Net 30","Incoterms":"CIF","OTIF %":91,"Quality PPM":520,"Audit Score":90,"Complaint Rate %":0.8,"Capacity Buffer %":14,"Supplier Capacity":1100000,"Commodity Volatility %":18,"Import Dependency %":22,"Supplier Concentration %":52,"Substitute Available":"Yes","Duty %":3,"Recyclability":92,"Certification":90,"Carbon Score":73,"EPR Readiness":78,"PCR Content %":0,"Mill Allocation %":82,"Moisture %":6.8,"Fibre Availability %":88,"Quality Continuity Score":92,"Corrugated Linkage":"Approved demonstration assumption"},
        {"Supplier":"Circular Paperworks Ltd","Material":"Kraft Paper","Kraft Variant":"Recycled Kraft","GSM":150,"Strength Grade":"22 BF","Quoted Unit Price USD":0.80,"Currency":"USD","Unit":"kg","MOQ":50000,"Lead Time Days":32,"Payment Terms":"Advance 20%","Incoterms":"FOB","OTIF %":86,"Quality PPM":1250,"Audit Score":76,"Complaint Rate %":2.7,"Capacity Buffer %":9,"Supplier Capacity":750000,"Commodity Volatility %":24,"Import Dependency %":10,"Supplier Concentration %":68,"Substitute Available":"No","Duty %":0,"Recyclability":98,"Certification":76,"Carbon Score":81,"EPR Readiness":80,"PCR Content %":95,"Mill Allocation %":92,"Moisture %":9.2,"Fibre Availability %":58,"Quality Continuity Score":68,"Corrugated Linkage":"Conditional demonstration assumption"},
    ])


def get_steel_demo_suppliers():
    """Return exactly three governed synthetic Steel supplier records for deterministic tests."""
    common = {
        "Material":"Steel","Unit":"kg",
        "Supported Steel Profiles":"CR_COIL_COMMERCIAL|GI_COIL_Z120|PPGI_COIL_Z120",
        "Controlled Grade Families":"CR commercial demonstration|GI substrate demonstration|PPGI substrate demonstration",
        "Thickness Min mm":0.45,"Thickness Max mm":0.90,"Width Min mm":1000,"Width Max mm":1250,
        "Zinc Capability Max g/m²":180,"Paint Line Capability":"Yes",
        "Surface Capability":"Controlled commercial|galvanized|pre-painted",
        "Coil Weight Min MT":4,"Coil Weight Max MT":15,
        "Supplier or Mill Approval":"Approved","Application Approval":"Approved",
        "Test Certificate Availability":"Available — not authenticated",
        "Source Label":"Synthetic controlled demonstration data",
        "Evidence Boundary":"Not audited supplier evidence; not live market data; not technical certification",
    }
    rows = [
        {**common,"Supplier":"Bharat Steelworks Ltd","Quoted Unit Price":1.08,"Currency":"USD","Quotation Currency":"USD","Quoted Unit Price USD":1.08,"MOQ":25000,"Lead Time Days":18,"Payment Terms":"Net 45","Incoterms":"DDP","OTIF %":95,"Quality PPM":620,"Audit Score":88,"Complaint Rate %":0.9,"Capacity Buffer %":18,"Supplier Capacity":1800000,"Capacity Utilisation %":76,"Mill Allocation %":72,"Import Dependency %":12,"Supplier Concentration %":38,"Quality Continuity Score":88,"Risk Category":"Low","Eligibility Design Intent":"Eligible competitive supplier"},
        {**common,"Supplier":"PrimeCoated Metals","Quoted Unit Price":96.30,"Currency":"INR","Quotation Currency":"INR","Quoted Unit Price USD":None,"MOQ":18000,"Lead Time Days":14,"Payment Terms":"Net 60","Incoterms":"DDP","OTIF %":97,"Quality PPM":420,"Audit Score":93,"Complaint Rate %":0.5,"Capacity Buffer %":24,"Supplier Capacity":1500000,"Capacity Utilisation %":68,"Mill Allocation %":64,"Import Dependency %":5,"Supplier Concentration %":28,"Quality Continuity Score":94,"Risk Category":"Low","Eligibility Design Intent":"Eligible higher-cost lower-risk supplier"},
        {**common,"Supplier":"Global Coil Trading","Quoted Unit Price":0.99,"Currency":"USD","Quotation Currency":"USD","Quoted Unit Price USD":0.99,"MOQ":50000,"Lead Time Days":42,"Payment Terms":"Advance 20%","Incoterms":"CIF","OTIF %":84,"Quality PPM":1450,"Audit Score":72,"Complaint Rate %":3.1,"Capacity Buffer %":6,"Supplier Capacity":2200000,"Capacity Utilisation %":94,"Mill Allocation %":95,"Import Dependency %":92,"Supplier Concentration %":78,"Quality Continuity Score":62,"Risk Category":"High","Application Approval":"Conditional","Test Certificate Availability":"Pending","Paint Line Capability":"No","Zinc Capability Max g/m²":100,"Coil Weight Min MT":16,"Coil Weight Max MT":25,"Eligibility Design Intent":"Lower-priced technically ineligible or conditional supplier"},
    ]
    data = pd.DataFrame(rows)
    data.attrs.update({
        "source_label":"Synthetic controlled demonstration data",
        "assumption_profile_version":"C3.1-STEEL-v1",
        "risk_assumption_basis":"Synthetic capability and continuity assumptions; not audited supplier evidence.",
        "market_data_boundary":"Not live market data.",
        "technical_boundary":"Not metallurgical certification, engineering approval or test-certificate authentication.",
    })
    return data


def get_raw_material_demo_suppliers(commodity="PET Resin"):
    if commodity == "Kraft Paper": return get_kraft_paper_demo_suppliers()
    if commodity == "Steel": return get_steel_demo_suppliers()
    prices={"PET Resin":1.27,"Polyethylene":1.34,"Polypropylene":1.30,"Aluminium Foil":3.18,"Copper":9.65}
    if commodity not in prices: raise ValueError(f"Unsupported synthetic raw-material commodity '{commodity}'.")
    base=prices[commodity]
    return pd.DataFrame([
        {"Supplier":"Indus Materials Ltd","Material":commodity,"Quoted Unit Price USD":round(base,3),"Currency":"USD","Unit":"kg","MOQ":20000,"Lead Time Days":21,"Payment Terms":"Net 45","Incoterms":"CIF","OTIF %":95,"Quality PPM":650,"Audit Score":86,"Complaint Rate %":1.0,"Capacity Buffer %":20,"Supplier Capacity":800000,"Commodity Volatility %":14,"Import Dependency %":45,"Supplier Concentration %":40,"Substitute Available":"Yes","Duty %":5,"Recyclability":75,"Certification":85,"Carbon Score":72,"EPR Readiness":70,"PCR Content %":15},
        {"Supplier":"Global Commodity Corp","Material":commodity,"Quoted Unit Price USD":round(base*.96,3),"Currency":"USD","Unit":"kg","MOQ":50000,"Lead Time Days":45,"Payment Terms":"Advance 20%","Incoterms":"FOB","OTIF %":88,"Quality PPM":1200,"Audit Score":76,"Complaint Rate %":2.8,"Capacity Buffer %":8,"Supplier Capacity":1200000,"Commodity Volatility %":28,"Import Dependency %":85,"Supplier Concentration %":70,"Substitute Available":"No","Duty %":8,"Recyclability":70,"Certification":75,"Carbon Score":65,"EPR Readiness":62,"PCR Content %":10},
        {"Supplier":"Bharat Advanced Polymers","Material":commodity,"Quoted Unit Price USD":round(base*1.04,3),"Currency":"USD","Unit":"kg","MOQ":10000,"Lead Time Days":12,"Payment Terms":"Net 60","Incoterms":"DDP","OTIF %":97,"Quality PPM":450,"Audit Score":91,"Complaint Rate %":0.6,"Capacity Buffer %":25,"Supplier Capacity":650000,"Commodity Volatility %":12,"Import Dependency %":20,"Supplier Concentration %":30,"Substitute Available":"Yes","Duty %":0,"Recyclability":80,"Certification":90,"Carbon Score":78,"EPR Readiness":76,"PCR Content %":18},
    ])


def get_demo_data(
    category="Packaging Procurement",
    commodity="Corrugated Board",
    selected_structure: str | None = None,
    expanded_supplier_pool: bool | None = None,
):
    if category=="Raw Material Procurement":
        data=get_raw_material_demo_suppliers(commodity)
    elif category=="Packaging Procurement" and commodity=="Flexible Laminates":
        if selected_structure is None: raise ValueError("Flexible Laminates demo data requires an explicit selected_structure.")
        data=get_flexible_laminate_demo_suppliers(selected_structure)
    else:
        data=get_demo_suppliers()

    if _expanded_pool_enabled(expanded_supplier_pool):
        if category == "Packaging Procurement" and commodity == "Flexible Laminates":
            base_price = {"PET / PE":2.05,"PET / MetPET / PE":2.38,"BOPP / CPP":1.92}[selected_structure]
            data = expand_flexible_laminates(data, base_price)
        elif category == "Raw Material Procurement" and commodity == "Kraft Paper":
            data = expand_kraft_paper(data)
        elif category == "Raw Material Procurement" and commodity == "Steel":
            data = expand_steel(data)
        elif category == "Packaging Procurement":
            data = expand_general_packaging(data)

    version = "C3.1-STEEL-v1" if commodity == "Steel" else ("C2.0" if commodity=="Flexible Laminates" else ("C1.0" if commodity=="Kraft Paper" else "S1"))
    source = "Synthetic controlled demonstration data" if commodity == "Steel" else "Synthetic demonstration data"
    data.attrs.update({"source_label":source,"assumption_profile_version":version,"category":category,"commodity":commodity})
    return data


def _read_uploaded_dataframe(uploaded_file):
    filename=str(getattr(uploaded_file,"name","") or "").strip(); suffix=filename.lower().rsplit(".",1)[-1] if "." in filename else ""
    if suffix not in {"csv","xlsx"}: raise RFQUploadError("Unsupported RFQ file type. Upload a .csv or .xlsx file exported as a standard table.")
    try: return pd.read_csv(uploaded_file) if suffix=="csv" else pd.read_excel(uploaded_file)
    except pd.errors.EmptyDataError as exc: raise RFQUploadError("The uploaded RFQ file is empty. Add a header row and at least one supplier quotation, then upload it again.") from exc
    except pd.errors.ParserError as exc: raise RFQUploadError("The CSV structure could not be parsed. Check delimiters, quotation marks and merged header rows, then export the file again.") from exc
    except (BadZipFile,ImportError) as exc: raise RFQUploadError("The Excel workbook could not be opened. Confirm that it is a valid .xlsx file and is not password-protected or corrupted.") from exc
    except (OSError,ValueError) as exc: raise RFQUploadError("The RFQ file could not be opened. Confirm that the file is not corrupted, password-protected or still open in another application.") from exc


def load_uploaded_rfq(uploaded_file):
    if uploaded_file is None: return None
    raw_df=_read_uploaded_dataframe(uploaded_file)
    if raw_df.empty: raise RFQUploadError("The uploaded RFQ contains headers but no supplier rows. Add at least one supplier quotation and upload it again.")
    try: normalized_df,report=normalize_rfq_dataframe(raw_df)
    except (KeyError,TypeError,ValueError) as exc: raise RFQUploadError("The RFQ columns could not be mapped reliably. Use one header row, remove merged cells and include clear supplier, price, MOQ, lead-time, payment-term and Incoterm columns.") from exc
    normalized_df.attrs["rfq_quality_report"]=report; normalized_df.attrs["source_label"]="Uploaded unverified supplier data"
    return normalized_df
