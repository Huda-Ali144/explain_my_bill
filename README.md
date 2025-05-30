# 🧾 Explain My Bill

**Explain My Bill** is a Streamlit app that helps anyone make sense of complex invoices—whether utilities, medical, credit-card, rent, insurance, or other bills. Just upload a PDF or image, correct any OCR glitches, and let Gemini AI walk you through every charge. Need more clarity? Ask follow-up questions in a built-in chat interface.

## Live Link
https://explainmybill.streamlit.app/

## Key Features

- **Accurate OCR**  
  Combines pdfplumber/PyMuPDF text extraction with GPU-accelerated EasyOCR and light preprocessing for crisp, clean text.

- **AI-Powered Summaries**  
  Choose between **Brief** (3-bullet overview) or **Detailed** (line-by-line walkthrough) explanations.

- **Interactive Q&A**  
  Drill deeper with a back-and-forth chat: ask about any line item, fees, due dates, anomalies, and the AI will respond in context.

- **Editable OCR Text**  
  Inline editor lets you fix mis-recognized lines before the AI sees them—ensuring you’re always getting accurate answers.

- **Category Auto-Detect**  
  Supports all bill types (utility, medical, financial, rent/mortgage, subscription, insurance). The AI can even guess the type for you.

- **Downloadable Outputs**  
  Export your AI explanation as a text file and grab an `.ics` reminder for due dates (coming soon!).

## Tech Stack

- **Streamlit** — fast, interactive web UI  
- **pdfplumber & PyMuPDF** — extract text from true-text PDFs  
- **EasyOCR** (GPU-enabled) — OCR for scanned/image PDFs  
- **Google Gemini API** — generative AI for explanations and chat  
- **OpenCV** — image preprocessing for better OCR  
- **Python 3.10+**

## Getting Started

1. **Clone & install**  
   git clone https://github.com/yourusername/explain-my-bill.git
   cd explain-my-bill
   pip install -r requirements.txt
2. **Set your API key**
   Add API Key to .streamlit/secrets.toml
   GEMINI_API_KEY = "your_actual_key_here"
3. **Run the app**
   streamlit run main.py

## 🙋‍♀️ Author
Built by [Huda Bhayani] – open to collaborations and improvements!