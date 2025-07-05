import pdfplumber
import fitz  # PyMuPDF
from pdfminer.high_level import extract_text
from pdf2image import convert_from_path
import pytesseract

PDF_PATH = "dekont.pdf"


def extract_pdfminer(pdf_path):
    print("=== pdfminer.six ile çıkarılıyor ===")
    text = extract_text(pdf_path)
    print(text[:1000])
    print()


if __name__ == "__main__":
  
    extract_pdfminer(PDF_PATH)
  
