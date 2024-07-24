from io import BytesIO
from flask import Flask, request, jsonify
import os
from PIL import Image
from frontend import index_html
from typress.model.model import load_model
from dotenv import load_dotenv

load_dotenv()

# app = Flask(__name__)
app = Flask("Typress OCR")

# Load model and processor
model, processor = load_model(os.getenv("MODEL_PATH"))


@app.route('/api/formula', methods=['POST'])
def get_formula():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image = request.files['image']
    img = Image.open(BytesIO(image.read()))
    try:
        pixel_values = processor(
            images=[img], return_tensors="pt").pixel_values
        generated_text = generate_formula(model, processor, pixel_values)
        return jsonify({"formula": generated_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/', methods=['GET'])
def index():
    return index_html()


if __name__ == '__main__':
    app.run(debug=True)
