from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from PIL import Image
from .frontend import index_html
from .model import load_model, generate, get_device
import os

current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
static_dir = os.path.join(current_dir, "frontend/dist")


def get_app(model_path, device, api_root):
    app = Flask(
        __name__,
        static_folder=static_dir,
        template_folder=static_dir,
        static_url_path="/",
    )
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
            pixel_values = processor(images=img, return_tensors="pt").pixel_values.to(
                device
            )
            generated_text = generate(model, processor, pixel_values)[0]
            return jsonify({"formula": generated_text})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/", methods=["GET"])
    def index():
        return render_template("index.html", api_root=api_root)

    return app
