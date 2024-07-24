from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
from .frontend import index_html
from .model import load_model, generate, get_device


def get_app(model_path, device, api_root):
    app = Flask("Typress OCR")
    CORS(app)

    # Load model and processor
    device = get_device(device)
    model, processor = load_model(model_path, device)

    @app.route("/api/formula", methods=["POST"])
    def get_formula():
        if "image" not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        image = request.files["image"]
        img = Image.open(image.stream).convert("RGB")
        try:
            pixel_values = processor(
                images=img,
                return_tensors="pt"
            ).pixel_values.to(device)
            generated_text = generate(model, processor, pixel_values)[0]
            return jsonify({"formula": generated_text})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/", methods=["GET"])
    def index():
        return index_html(api_root)

    # app.run(host=host, port=port)
    return app
