# File: main.py

import os
import streamlit as st
from bill_ocr import extract_text_from_file
from ai_explainer import get_ai_explanation, get_followup_explanation

st.set_page_config(
    page_title="🧾 Explain My Bill",
    page_icon="💡",
    layout="centered"
)

# --- Caching wrappers ---
@st.cache_data(show_spinner=False)
def cached_extract_text(path: str) -> str:
    try:
        return extract_text_from_file(path)
    except Exception as e:
        st.error(f"Text extraction failed: {e}")
        return ""

@st.cache_data(show_spinner=False)
def cached_ai_explain(text: str, level: str, category: str) -> str:
    try:
        return get_ai_explanation(text, level=level.lower(), category=category)
    except Exception as e:
        st.error(f"AI explanation failed: {e}")
        return ""

@st.cache_data(show_spinner=False)
def cached_followup(text: str, prev: str, question: str, level: str, category: str) -> str:
    try:
        return get_followup_explanation(
            text,
            prev,
            question,
            level=level.lower(),
            category=category
        )
    except Exception as e:
        st.error(f"Follow-up failed: {e}")
        return ""

# --- File saving helper ---
def save_uploaded_file(uploaded, folder: str = "uploads") -> str:
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, uploaded.name)
    with open(path, "wb") as f:
        f.write(uploaded.getbuffer())
    return path

def main():
    st.title("🧾 Explain My Bill")
    st.write("Upload a PDF or image of your bill and get a plain-English breakdown, with follow-up Q&A.")

    # 1) Upload
    uploaded = st.file_uploader("Choose file:", type=["pdf","png","jpg","jpeg"])
    if not uploaded:
        st.info("Waiting for you to upload a bill…")
        return

    # 2) OCR
    file_path = save_uploaded_file(uploaded)
    with st.spinner("Extracting text…"):
        bill_text = cached_extract_text(file_path)
    if not bill_text:
        st.error("No text extracted. Try another file.")
        return

    # 3) Editable OCR text
    with st.expander("View & Edit Extracted Text"):
        st.text_area(
            "📝 Edit OCR text if needed:",
            value=bill_text,
            height=300,
            key="edited_text"
        )
    ocr_input = st.session_state.get("edited_text", bill_text)

    # 4) Bill category & detail level
    bill_type = st.selectbox(
        "Bill category:",
        ["Auto-detect","Utility","Medical","Financial (Credit Card/Bank)",
         "Rent/Mortgage","Subscription","Insurance","Other"]
    )
    detail_level = st.selectbox(
        "Explanation level:",
        ["Brief","Detailed"]
    )

    # 5) Initial explanation
    if st.button("🤖 Explain My Bill"):
        with st.spinner("Analyzing with AI…"):
            explanation = cached_ai_explain(ocr_input, detail_level, bill_type)
        st.session_state["initial_explanation"] = explanation
        st.subheader("💡 AI Explanation")
        st.markdown(explanation)
        st.download_button(
            "📥 Download Explanation",
            data=explanation,
            file_name="bill_explanation.txt",
            mime="text/plain"
        )

    # 6) Follow-up Q&A
    if "initial_explanation" in st.session_state:
        st.write("---")
        st.subheader("🔄 Ask a Follow-Up Question")
        question = st.text_input("Your question:", key="followup_input")
        if question:
            with st.spinner("Getting follow-up…"):
                followup = cached_followup(
                    ocr_input,
                    st.session_state["initial_explanation"],
                    question,
                    detail_level,
                    bill_type
                )
            st.markdown("**Follow-Up Answer:**")
            st.write(followup)

if __name__ == "__main__":
    main()