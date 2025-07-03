from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import os

# Set your Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_pdf(pdf_path):
    pages = convert_from_path(pdf_path)
    full_text = ""
    for i, page in enumerate(pages):
        temp_img = f"page_{i}.jpg"
        page.save(temp_img, "JPEG")
        text = pytesseract.image_to_string(Image.open(temp_img))
        full_text += text + "\n"
        os.remove(temp_img)
    return full_text

def extract_text_from_image(img_path):
    return pytesseract.image_to_string(Image.open(img_path))
