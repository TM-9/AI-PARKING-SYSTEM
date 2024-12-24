from flask import Flask, render_template, jsonify, Response
import cv2
import easyocr
from datetime import datetime
from database import Database
from sensor import detect_entry_exit  # Simulated sensor logic
from ultralytics import YOLO  # Import YOLOv8 from ultralytics

app = Flask(__name__)

# Initialize the database
db = Database()

# Initialize EasyOCR
reader = easyocr.Reader(['en'])

# Load YOLOv8n model (use your custom model if trained)
model = YOLO(r'C:\Users\taimo\Desktop\AI_project\runs\detect\train4\weights\best.pt')  # Replace with the path to your trained YOLOv8n model

# Initialize live camera feed (use webcam or replace with IP camera URL)
camera_url =0 # "http://192.168.1.102:8080/video"  # Replace with
cap = cv2.VideoCapture(camera_url)

if not cap.isOpened():
    raise RuntimeError("Error: Could not access the camera.")
else:
    print("Camera is ready.")

def detect_and_recognize_plate(frame):
    # Convert frame to RGB (YOLO expects RGB input)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Perform inference with YOLOv8n model
    results = model(rgb_frame)

    # Parse the results to get bounding boxes and labels
    plates = results[0].boxes  # Get the boxes detected in the image

    plate_number = "Unknown"

    # Loop through the detections
    for box in plates:
        x1, y1, x2, y2 = map(int, box.xyxy[0])  # Get coordinates of the bounding box
        confidence = box.conf[0]  # Confidence score for the detection
        class_id = int(box.cls[0])  # Class ID of the detection

        # Check if the detection is a license plate (assuming class 0 for license plates)
        if class_id == 0 and confidence >0.7 :  # Adjust confidence threshold as needed
            # Crop the detected plate region
            plate_region = frame[y1:y2, x1:x2]

            # Use EasyOCR to read the license plate text
            try:
                result = reader.readtext(plate_region)
                if result:
                    plate_number = result[0][1]
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, plate_number, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                    # Store the plate in the database
                    db.add_detected_plate(plate_number)
            except Exception as e:
                print(f"Error during OCR: {e}")

    return plate_number

def generate_frames():
    while True:
        success, frame = cap.read()
        if not success:
            break

        detect_and_recognize_plate(frame)

        # Encode the frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    plates = db.get_all_detected_plates()
    return render_template('index.html', plates=plates)

@app.route('/log_car', methods=['POST'])
def log_car():
    car_id = detect_and_recognize_plate(cap.read()[1])
    action = detect_entry_exit()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if action == "entry":
        db.add_car_entry(car_id, timestamp)
    else:
        db.add_car_exit(car_id, timestamp)

    return jsonify({"status": "success", "action": action, "car_id": car_id, "timestamp": timestamp})

import atexit
@atexit.register
def cleanup():
    if cap.isOpened():
        cap.release()
        print("Camera released.")

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
