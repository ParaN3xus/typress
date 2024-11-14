import mimetypes

mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("text/css", ".css")

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from PIL import Image
from .model.typressmodel import typressmodel
import os
import json

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
    model = typressmodel(None, model_path, device)

    @app.route("/api/rec", methods=["POST"])
    def recognize():
        if "image" not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        if "bbox" not in request.form:
            return jsonify({"error": "No bbox data provided"}), 400
        
        try:
            image = request.files["image"]
            bbox = request.form["bbox"]
            bbox_data = json.loads(bbox)
            generated_text = model.recognize(image.stream, bbox_data)
            return jsonify({"formula": generated_text})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    @app.route("/api/det", methods=["POST"])
    def detect():
        if "image" not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        image = request.files["image"]
        try:
            bboxes = model.detect(image.stream)
            return jsonify({"bboxes": bboxes})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/", methods=["GET"])
    def index():
        return render_template("index.html", api_root=api_root)

    return app
