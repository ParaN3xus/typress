from flask import Flask, request, jsonify
import os
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
    try:
        pixel_values = processor(
            images=[image], return_tensors="pt").pixel_values
        generated_text = generate_formula(model, processor, pixel_values)
        return jsonify({"formula": generated_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
