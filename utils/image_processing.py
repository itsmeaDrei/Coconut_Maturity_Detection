import os
import cv2
from ultralytics import YOLO

# Path to the YOLOv5 model weights
MODEL_PATH = "yoloversions/yolov5.pt"
try:
    model = YOLO(MODEL_PATH)
    print(f"Model loaded from {MODEL_PATH}")
except Exception as e:
    model = None
    print(f"Error loading model: {e}")

#Loads an image, performs object detection using YOLO, counts objects by stage,
# draws bounding boxes, saves the processed image, and returns detection results.
def process_uploaded_image(filepath, processed_folder):
    if not model:
        return {"error": "Model not loaded."}

    try:
        img = cv2.imread(filepath)
        if img is None:
            return {"error": "Failed to read image."}

        img_height, img_width = img.shape[:2]
        results = model.predict(filepath, conf=0.40)
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
            cropped_img = img[crop_top:crop_bottom, crop_left:crop_right]
        else:
            cropped_img = img
            crop_left = crop_top = 0

        img_cv = cropped_img.copy()

        stage1_count = stage2_count = stage3_count = 0
        confidence = []

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

            confidence.append(box.conf[0].item())
            if label == "stage1":
                stage1_count += 1
            elif label == "stage2":
                stage2_count += 1
            elif label == "stage3":
                stage3_count += 1

        average_confidence = sum(confidence) / len(confidence) if confidence else 0

        processed_img_path = os.path.join(processed_folder, "processed.jpg")
        cv2.imwrite(processed_img_path, img_cv)

        return {
            "image_url": f"/processed-image?t={int(os.path.getmtime(processed_img_path))}",
            "results": {
                "stage1": stage1_count,
                "stage2": stage2_count,
                "stage3": stage3_count,
                "total": len(boxes),
                "confidence": round(average_confidence * 100, 2)
            }
        }

    except Exception as e:
        return {"error": str(e)}
