from ultralytics import YOLO
from config import MODEL_PATH

#Loads YOLO model from MODEL_PATH.
def load_model():
    try:
        model = YOLO(MODEL_PATH)
        print(f"✅ Model loaded: {MODEL_PATH}")
        return model
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None
