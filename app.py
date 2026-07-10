# =====================================================
# AI PROCUREMENT COPILOT
# Portfolio Edition v1.0
# Build 0.1 — Repository Foundation
# =====================================================

import streamlit as st


st.set_page_config(
    page_title="AI Procurement Copilot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.title("AI Procurement Copilot")
st.subheader("Portfolio Edition v1.0")

st.info(
    "Build 0.1 establishes the repository foundation, project governance, recovery system, and initial app skeleton. "
    "Procurement logic will be added in upcoming builds."
)

st.markdown("---")

st.header("Project Vision")
st.write(
    "AI Procurement Copilot is a transparent, rule-guided, AI-ready procurement decision platform for RFQ analysis, "
    "packaging should-cost, advanced TCO, supplier risk, ESG, allocation, negotiation, and executive sourcing recommendations."
)

st.header("Current Build")
st.write("**Build:** 0.1 — Repository Foundation")
st.write("**Status:** In Development")
st.write("**Next Build:** 0.2 — Streamlit Framework and Modular Application Skeleton")

st.header("Architecture Direction")
st.code(
    """
AI Procurement Copilot
├── Presentation Layer: Streamlit
├── Procurement Decision Engine
├── Category Engine: Packaging v1.0
├── Future Category Engine: Raw Materials v1.1
├── Business Rules Layer
├── AI Assistance Layer
├── Data Layer
└── Documentation + Recovery Layer
    """,
    language="text",
)
