import os
from utils.ocr import extract_text_from_pdf, extract_text_from_image

def get_input_text():
    print("\nChoose input method:")
    print("1. Type or paste medical text")
    print("2. Upload PDF report")
    print("3. Upload Image report")
    
    choice = input("Enter choice (1/2/3): ")

    if choice == "1":
        print("Paste your report text below (end with a blank line):")
        lines = []
        while True:
            line = input()
            if not line.strip():
                break
            lines.append(line)
        return "\n".join(lines)

    elif choice == "2":
        path = input("Enter full path to the PDF file: ").strip()
        return extract_text_from_pdf(path)

    elif choice == "3":
        path = input("Enter full path to the image file: ").strip()
        return extract_text_from_image(path)

    else:
        print("Invalid choice.")
        return None

# ✅ Add these two helper methods so app.py can use them directly
def get_text_from_pdf(path):
    return extract_text_from_pdf(path)

def get_text_from_image(path):
    return extract_text_from_image(path)
