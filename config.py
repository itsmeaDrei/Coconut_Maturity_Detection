import os

UPLOAD_FOLDER = "static/uploads"
PROCESSED_FOLDER = "static/processed"
MODEL_PATH = "yolov5.pt"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
