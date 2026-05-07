"""
Streamlit Web UI for AI Document OCR & NLP Pipeline
Upload documents and extract structured data in real-time
"""

import streamlit as st
import json
import tempfile
import os
from pathlib import Path
from src.ocr_pipeline import DocumentOCRPipeline

st.set_page_config(
    page_title="AI Document OCR & NLP",
    page_icon="📄",
    layout="wide"
)

st.title("📄 AI Document OCR & NLP Pipeline")
st.markdown(
    "**Extract structured data from invoices, receipts, and contracts using AI-powered OCR**"
)
st.divider()

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    doc_type = st.selectbox(
        "Document Type",
        ["Auto-Detect", "invoice", "receipt", "contract", "general"],
        index=0
    )
    show_raw = st.checkbox("Show Raw OCR Text", value=False)
    st.markdown("---")
    st.markdown("**Supported Formats**")
    st.markdown("✅ PDF  ✅ PNG  ✅ JPG  ✅ TIFF")
    st.markdown("---")
    st.markdown("Built by [Sheraz Karim](https://www.upwork.com/freelancers/sherazkarim)")

# Upload
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📤 Upload Document")
    uploaded_file = st.file_uploader(
        "Drop your document here",
        type=["pdf", "png", "jpg", "jpeg", "tiff", "bmp"]
    )

    if uploaded_file:
        st.success(f"✅ Uploaded: **{uploaded_file.name}**")

        if st.button("🚀 Extract Data", type="primary", use_container_width=True):
            with st.spinner("🔍 Running OCR & AI extraction..."):
                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=Path(uploaded_file.name).suffix
                ) as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name

                try:
                    pipeline = DocumentOCRPipeline()
                    selected_type = None if doc_type == "Auto-Detect" else doc_type
                    result = pipeline.process(tmp_path, selected_type, save_output=False)
                    st.session_state["result"] = result
                    st.session_state["raw_text"] = pipeline.extracted_text
                    st.success("✅ Extraction complete!")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                finally:
                    os.unlink(tmp_path)

with col2:
    st.subheader("📊 Extracted Data")

    if "result" in st.session_state:
        result = st.session_state["result"]
        st.info(f"**Document Type:** {result['document_type'].upper()}  |  "
                f"**Text Length:** {result['raw_text_length']} chars")

        extracted = result["extracted_data"]
        st.json(extracted)

        col_a, col_b = st.columns(2)
        with col_a:
            st.download_button(
                "⬇️ Download JSON",
                data=json.dumps(result, indent=2),
                file_name="extracted_data.json",
                mime="application/json",
                use_container_width=True
            )

if show_raw and "raw_text" in st.session_state:
    st.divider()
    st.subheader("🔤 Raw OCR Text")
    st.text_area("OCR Output", st.session_state["raw_text"], height=300)

# Demo section
if "result" not in st.session_state:
    st.divider()
    st.subheader("💡 What This Tool Extracts")
    demo_col1, demo_col2, demo_col3 = st.columns(3)
    with demo_col1:
        st.markdown("**📃 Invoices**")
        st.markdown("- Invoice number & dates\n- Vendor & client info\n- Line items & totals\n- Tax & discounts\n- Payment terms")
    with demo_col2:
        st.markdown("**🧾 Receipts**")
        st.markdown("- Store name & date\n- Itemized purchases\n- Tax & total\n- Payment method\n- Receipt number")
    with demo_col3:
        st.markdown("**📋 Contracts**")
        st.markdown("- Parties & dates\n- Contract value\n- Key obligations\n- Payment terms\n- Termination clauses")
