from io import BytesIO
from flask import Flask, request, jsonify
import os
from PIL import Image
from frontend import index_html
from typress.model.model import load_model, generate
from dotenv import load_dotenv
import torch

load_dotenv()

# app = Flask(__name__)
app = Flask("Typress OCR")

# Load model and processor
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model, processor = load_model(os.getenv("MODEL_PATH"))
model.to(device)


@app.route("/api/formula", methods=["POST"])
def get_formula():
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image = request.files["image"]
    img = Image.open(image).convert("RGB")
    try:
        pixel_values = processor(images=img, return_tensors="pt").pixel_values.to(
            device
        )
        generated_text = generate(model, processor, pixel_values)[0]
        return jsonify({"formula": generated_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def index():
    return index_html()


if __name__ == "__main__":
    app.run(debug=True)
