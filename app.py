from flask import Flask, request, render_template, send_from_directory, jsonify
import os
import cv2
import numpy as np
from ultralytics import YOLO

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
PROCESSED_FOLDER = "static/processed"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["PROCESSED_FOLDER"] = PROCESSED_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

MODEL_PATH = "coconutv4(detection).pt"  # Replace with your model path

try:
    model = YOLO(MODEL_PATH)
    print(f"✅ Model loaded successfully from: {MODEL_PATH}")
    print(f"✅ Model class names: {model.names}")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze_image():
    if not model:
        return jsonify({"error": "Model not loaded."}), 500

    if "file" not in request.files or request.files["file"].filename == "":
        return jsonify({"error": "No file selected."}), 400

    file = request.files["file"]
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], "uploaded.jpg")
    file.save(filepath)
    print(f"✅ Image saved: {filepath}")

    if not os.path.exists(filepath):
        return jsonify({"error": "File save failed."}), 500

    try:
        img = cv2.imread(filepath)
        if img is None:
            return jsonify({"error": "Failed to read image with OpenCV."}), 400
        img_height, img_width = img.shape[:2]  # Get image dimensions

        results = model.predict(filepath, conf=0.40)  # Use filepath directly
        result = results[0]
        boxes = result.boxes
        class_names = model.names

        x1s, y1s, x2s, y2s = [], [], [], []
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            x1s.append(x1)
            y1s.append(y1)
            x2s.append(x2)
            y2s.append(y2)

        if boxes.xyxy.shape[0] > 0:
            crop_left = max(min(x1s), 0)
            crop_top = max(min(y1s), 0)
            crop_right = min(max(x2s), img_width)
            crop_bottom = min(max(y2s), img_height)
            cropped_img = img[crop_top:crop_bottom, crop_left:crop_right]  # Slicing for crop
        else:
            cropped_img = img
            crop_left = crop_top = 0
            print("No objects detected in the image.")

        img_cv = cropped_img.copy()  # Work on a copy

        for box in boxes:
            x_center, y_center, w, h = box.xywh[0].tolist()
            cls_id = int(box.cls[0])
            label = class_names[cls_id] if class_names else f"id:{cls_id}"

            x = int(x_center) - crop_left
            y = int(y_center) - crop_top
            w = int(w)
            h = int(h)

            x1 = max(x - w // 2, 0)
            y1 = max(y - h // 2, 0)
            x2 = min(x + w // 2, img_cv.shape[1])
            y2 = min(y + h // 2, img_cv.shape[0])

            cv2.rectangle(img_cv, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img_cv, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        processed_img_path = os.path.join(app.config["PROCESSED_FOLDER"], "processed.jpg")
        cv2.imwrite(processed_img_path, img_cv)
        print(f"✅ Processed image saved: {processed_img_path}")

        # --- COUNTING LOGIC ---
        stage1_count = 0
        stage2_count = 0
        stage3_count = 0

        for box in boxes:
            cls_id = int(box.cls[0])
            label = class_names[cls_id] if class_names else f"id:{cls_id}"

            if label == "stage1":
                stage1_count += 1
            elif label == "stage2":
                stage2_count += 1
            elif label == "stage3":
                stage3_count += 1

        results_data = {
            "stage1": stage1_count,
            "stage2": stage2_count,
            "stage3": stage3_count,
            "total": len(boxes)
        }

        return jsonify({
            "image_url": f"/processed-image?t={int(os.path.getmtime(processed_img_path))}",
            "results": results_data
        })

    except Exception as e:
        print(f"❌ Processing error: {e}")
        return jsonify({"error": f"Image processing error: {e}"}), 500


@app.route("/processed-image")
def get_processed_image():
    return send_from_directory(app.config["PROCESSED_FOLDER"], "processed.jpg", mimetype="image/jpeg")


if __name__ == "__main__":
    app.run(debug=True)