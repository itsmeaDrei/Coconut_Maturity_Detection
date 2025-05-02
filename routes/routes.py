from flask import Blueprint, request, render_template, send_from_directory, jsonify, current_app
from utils.image_processing import process_uploaded_image
import os

# Create a Blueprint named 'main'
main = Blueprint("main", __name__)

# Home page route
@main.route("/")
def index():
    return render_template("index.html")

# Route to analyze uploaded image
#Handles image analysis upon POST request.
@main.route("/analyze", methods=["POST"])
def analyze_image():
    if "file" not in request.files or request.files["file"].filename == "":
        return jsonify({"error": "No file selected."}), 400

    file = request.files["file"]
    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], "uploaded.jpg")
    file.save(filepath)

    if not os.path.exists(filepath):
        return jsonify({"error": "File save failed."}), 500

    result = process_uploaded_image(filepath, current_app.config["PROCESSED_FOLDER"])
    if "error" in result:
        return jsonify({"error": result["error"]}), 500

    return jsonify(result)

# Sends the processed image file
@main.route("/processed-image")
def get_processed_image():
    return send_from_directory(current_app.config["PROCESSED_FOLDER"], "processed.jpg", mimetype="image/jpeg")
