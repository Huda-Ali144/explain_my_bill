# File: bill_ocr.py

import os
import cv2
import numpy as np
from pdf2image import convert_from_path
from PIL import Image
import easyocr
from concurrent.futures import ThreadPoolExecutor

# Optional PDF text-extraction
try:
    import pdfplumber
except ImportError:
    pdfplumber = None

# EasyOCR reader (enable GPU if available)
reader = easyocr.Reader(['en'], gpu=False)


def preprocess_for_ocr(img: np.ndarray) -> np.ndarray:
    """
    Light preprocessing: convert to grayscale, mild upscale if small,
    then apply Otsu threshold for speed.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    if max(h, w) < 1000:
        gray = cv2.resize(gray, (0, 0), fx=1.5, fy=1.5,
                          interpolation=cv2.INTER_LINEAR)
    _, thresh = cv2.threshold(gray, 0, 255,
                              cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh


def clean_ocr_text(text: str) -> str:
    """
    Remove noisy lines: empty, single repeated chars, or mostly non-alphanumeric.
    """
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        s = line.strip()
        if not s:
            continue
        # skip lines with one repeated character
        if len(set(s)) == 1:
            continue
        # skip lines with >50% non-alphanumeric chars
        non_alnum = sum(1 for c in s if not c.isalnum())
        if non_alnum / len(s) > 0.5:
            continue
        cleaned.append(s)
    return "\n".join(cleaned)


def extract_text_from_image(path: str) -> str:
    """
    OCR a single image file and return cleaned text.
    """
    try:
        img = cv2.imread(path)
        if img is None:
            pil = Image.open(path).convert("RGB")
            img = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
        proc = preprocess_for_ocr(img)
        text = "\n".join(reader.readtext(proc, detail=0, paragraph=True))
        return clean_ocr_text(text)
    except Exception as e:
        return f"[Error in image OCR] {e}"


def extract_text_from_pdf(path: str, dpi: int = 150) -> str:
    """
    1) Try pdfplumber for true-text PDFs.
    2) If that fails, rasterize pages at lower DPI and OCR in parallel.
    """
    # 1) pdfplumber text extraction
    if pdfplumber:
        try:
            pages_txt = []
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    txt = page.extract_text()
                    if txt:
                        pages_txt.append(txt)
            if pages_txt:
                return clean_ocr_text("\n\n".join(pages_txt))
        except Exception:
            pass

    # 2) Rasterize and OCR
    try:
        images = convert_from_path(path, dpi=dpi)
    except Exception as e:
        return f"[Error in PDF rasterization] {e}"

    def ocr_page(page_image):
        img_cv = cv2.cvtColor(np.array(page_image), cv2.COLOR_RGB2BGR)
        proc = preprocess_for_ocr(img_cv)
        page_text = "\n".join(reader.readtext(proc, detail=0, paragraph=True))
        return clean_ocr_text(page_text)

    with ThreadPoolExecutor() as executor:
        pages = list(executor.map(ocr_page, images))

    return "\n\n".join(pages)


def extract_text_from_file(file_path: str) -> str:
    """
    Dispatch based on file extension.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in {".png", ".jpg", ".jpeg", ".tiff"}:
        return extract_text_from_image(file_path)
    else:
        return f"Unsupported file type: {ext}"