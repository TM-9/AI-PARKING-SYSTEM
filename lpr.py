import easyocr
import cv2

from app import cap


def recognize_license_plate_from_frame(frame):
    # Capture a frame from the camera feed
    ret, frame = cap.read()
    if not ret or frame is None:
        print("Error: Could not read frame.")
    else:
        # Pass the frame through the license plate recognition function
        plate = recognize_license_plate_from_frame(frame)
        print(f"Detected Plate: {plate}")

    # Initialize EasyOCR reader
    reader = easyocr.Reader(['en'])

    # Preprocessing steps to enhance OCR performance
    # 1. Convert the image to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 2. Apply thresholding to make the text more prominent
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    # 3. Apply Gaussian Blur to reduce noise
    blurred = cv2.GaussianBlur(thresh, (5, 5), 0)

    # 4. Optionally resize the image to improve OCR (adjust the size as needed)
    resized_frame = cv2.resize(blurred, (640, 480))  # Resize to a standard size (adjustable)

    # Process the frame for text using EasyOCR
    result = reader.readtext(resized_frame)

    # Check for detected license plate text
    for detection in result:
        text = detection[1]  # Detected text (license plate)
        print(f"Detected License Plate: {text}")
        return text

    return "Unknown"  # Return "Unknown" if no plate is detected