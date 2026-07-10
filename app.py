# =====================================================
# AI PROCUREMENT COPILOT
# Portfolio Edition v1.0
# Build 0.2 — Streamlit Framework and Modular Skeleton
# =====================================================

import streamlit as st

from modules.config import APP_NAME, EDITION, BUILD, STATUS
from modules.data_loader import get_demo_suppliers, load_uploaded_rfq
from modules.dashboard import render_executive_dashboard, render_supplier_snapshot
from modules.rfq import validate_rfq_columns
from modules.sidebar import render_sidebar


st.set_page_config(
    page_title=APP_NAME,
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


assumptions = render_sidebar()

st.title(APP_NAME)
st.subheader(EDITION)

st.info(
    "Build 0.2 establishes the modular Streamlit framework. "
    "Full procurement scoring engines will be added in Build 0.3."
)

st.markdown("---")

uploaded_file = None
if assumptions["data_source"] == "Upload RFQ CSV/Excel":
    uploaded_file = st.file_uploader("Upload RFQ CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None:
    suppliers_df = load_uploaded_rfq(uploaded_file)
    missing_columns = validate_rfq_columns(suppliers_df)
    if missing_columns:
        st.warning(f"Uploaded file is missing expected columns: {', '.join(missing_columns)}")
else:
    suppliers_df = get_demo_suppliers()

render_executive_dashboard(suppliers_df, assumptions)
render_supplier_snapshot(suppliers_df)

st.markdown("---")

st.header("Build Status")
st.write(f"**Current Build:** {BUILD}")
st.write(f"**Status:** {STATUS}")
st.write("**Next Build:** Build 0.3 — Packaging Procurement Engines")

st.header("Architecture Direction")
st.code(
    """
AI Procurement Copilot
├── app.py
├── modules/
│   ├── config.py
│   ├── data_loader.py
│   ├── sidebar.py
│   ├── dashboard.py
│   ├── rfq.py
│   ├── should_cost.py
│   ├── tco.py
│   ├── risk.py
│   ├── esg.py
│   ├── performance.py
│   ├── allocation.py
│   ├── negotiation.py
│   ├── recommendation.py
│   ├── charts.py
│   └── utils.py
└── docs + sample_data + tests
    """,
    language="text",
)
