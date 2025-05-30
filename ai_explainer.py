# File: ai_explainer.py

import streamlit as st
import google.generativeai as genai

# 1) Load your Gemini API key from Streamlit secrets
API_KEY = st.secrets.get("GEMINI_API_KEY")
if not API_KEY:
    st.error("❌ Please add GEMINI_API_KEY to .streamlit/secrets.toml")
    st.stop()

# 2) Configure the Gemini client
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


def _build_prompt(
    bill_text: str,
    level: str,
    category: str,
    include_explanation: str = None,
    followup: str = None
) -> str:
    """
    Construct either the initial explanation prompt or a follow-up prompt.
    """
    lvl = level.lower()
    cat = category

    # Category context
    if cat.lower() == "auto-detect":
        cat_instr = (
            "First identify the type of this bill "
            "(e.g. Utility, Medical, Financial, Rent, Subscription, Insurance, etc.)."
        )
        cat_desc = "any bill"
    else:
        cat_instr = f"This is a {cat} bill."
        cat_desc = cat.lower()

    if followup:
        # Follow-up prompt
        return f"""
You are an AI assistant that simplifies {cat_desc}.
Here is the bill text:
\"\"\"
{bill_text}
\"\"\"

Here is the previous AI explanation:
\"\"\"
{include_explanation}
\"\"\"

A user follow-up question:
\"\"\"
{followup}
\"\"\"

Answer the follow-up question clearly and concisely, referencing the bill text as needed.
"""
    else:
        # Initial explanation prompt
        if lvl == "brief":
            instr = (
                "Provide a very concise summary in 3 bullet points covering:\n"
                "  • What the bill is for\n"
                "  • Total amount due and key fees\n"
                "  • Any unusual charges"
            )
        else:
            instr = (
                "Walk me through every line item in plain English, including:\n"
                "  1. What each charge represents\n"
                "  2. Subtotals, taxes, fees\n"
                "  3. Due dates or late-fee rules\n"
                "Also, note anything that seems unusually high or unclear."
            )

        return f"""
You are an AI assistant that simplifies {cat_desc}.
{cat_instr}

Here is the bill text:
\"\"\"
{bill_text}
\"\"\"

{instr}

Be {'concise' if lvl=='brief' else 'thorough'}, clear, and organized.
"""


def get_ai_explanation(
    bill_text: str,
    level: str = "detailed",
    category: str = "Auto-detect"
) -> str:
    """
    Generate the initial explanation for a bill.
    """
    prompt = _build_prompt(bill_text, level, category)
    try:
        resp = model.generate_content(prompt)
        return resp.text.strip()
    except Exception as e:
        return f"❌ Gemini API Error: {e}"


def get_followup_explanation(
    bill_text: str,
    previous_explanation: str,
    followup_question: str,
    level: str = "detailed",
    category: str = "Auto-detect"
) -> str:
    """
    Generate an answer to a follow-up question, given the original bill text
    and the previous explanation.
    """
    prompt = _build_prompt(
        bill_text,
        level,
        category,
        include_explanation=previous_explanation,
        followup=followup_question
    )
    try:
        resp = model.generate_content(prompt)
        return resp.text.strip()
    except Exception as e:
        return f"❌ Gemini API Error: {e}"