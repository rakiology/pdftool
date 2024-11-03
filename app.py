from flask import Flask, request, render_template, jsonify
import fitz  # PyMuPDF
from PIL import Image
import io
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def extract_text_from_pdf(pdf_path):
    with fitz.open(pdf_path) as pdf:
        text = ""
        pages = []
        for page_num, page in enumerate(pdf, start=1):
            page_text = page.get_text()
            pages.append({
                "page_number": page_num,
                "content": page_text
            })
        return pages

def extract_images_from_pdf(pdf_path):
    images = []
    with fitz.open(pdf_path) as pdf:
        for page_num in range(len(pdf)):
            for img_index, img in enumerate(pdf.get_page_images(page_num), start=1):
                xref = img[0]
                base_image = pdf.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                image = Image.open(io.BytesIO(image_bytes))
                image_path = f"static/extracted_image_page{page_num + 1}_{img_index}.{image_ext}"
                image.save(image_path)
                images.append({
                    "page": page_num + 1,
                    "image_index": img_index,
                    "image_url": image_path
                })
    return images

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if 'pdf_file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400
        
        file = request.files['pdf_file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            # Extract text and images
            text_data = extract_text_from_pdf(file_path)
            image_data = extract_images_from_pdf(file_path)

            # Create JSON response
            response_data = {
                "filename": file.filename,
                "pages": text_data,
                "images": image_data
            }

            # Check if the client wants JSON or HTML
            if request.headers.get('Accept') == 'application/json':
                return jsonify(response_data)
            else:
                return render_template("result.html", data=response_data)

    return render_template("upload.html")

if __name__ == "__main__":
    app.run(debug=True)
