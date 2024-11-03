import fitz  # PyMuPDF
from PIL import Image
import io
import json

def extract_text_from_pdf(pdf_path):
    with fitz.open(pdf_path) as pdf:
        text = ""
        for page_num, page in enumerate(pdf, start=1):
            page_text = page.get_text()
            text += f"\nPage {page_num}:\n{page_text}"
        return text

def extract_images_from_pdf(pdf_path):
    images = []
    with fitz.open(pdf_path) as pdf:
        for page_num in range(len(pdf)):
            for img_index, img in enumerate(pdf.get_page_images(page_num), start=1):
                xref = img[0]
                base_image = pdf.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                # Create an Image object using Pillow and save it
                image = Image.open(io.BytesIO(image_bytes))
                image_path = f"extracted_image_page{page_num + 1}_{img_index}.{image_ext}"
                image.save(image_path)
                
                images.append({
                    "page": page_num + 1,
                    "image_index": img_index,
                    "image_path": image_path
                })
    return images

# Specify PDF file path
pdf_path = "file.pdf"

# Extract text
text_data = extract_text_from_pdf(pdf_path)
print("Extracted Text:")
print(text_data)

# Extract images
image_data = extract_images_from_pdf(pdf_path)
print("Extracted Images:", json.dumps(image_data, indent=4))

# Save text and images in JSON format
output_data = {
    "text": text_data,
    "images": image_data
}

with open("extracted_pdf_data.json", "w", encoding="utf-8") as f:
    json.dump(output_data, f, ensure_ascii=False, indent=4)

print("\nData extraction complete. Text and image information saved in 'extracted_pdf_data.json'.")
