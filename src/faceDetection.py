import cv2
import numpy as np
import json
import time

# Adjust the resolution for faster processing
TARGET_RESOLUTION = (640, 480)

# Initialize face classifier
face_classifier = cv2.CascadeClassifier("src/haarcascade_frontalface_default.xml")
video_cam = cv2.VideoCapture(0)

if not video_cam.isOpened():
    print("Cannot access the camera")
    exit()

# Get the original resolution
original_height = int(video_cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

prev_center_y = None
alpha = 0.3  # Smoothing factor

def process_frame(frame):
    global prev_center_y
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    if len(faces) > 0:
        (x, y, w, h) = max(faces, key=lambda f: f[2] * f[3])
        current_center_y = y + h // 2

        if prev_center_y is None:
            smooth_center_y = current_center_y
        else:
            smooth_center_y = int(alpha * current_center_y + (1 - alpha) * prev_center_y)

        prev_center_y = smooth_center_y

        # Normalize the y-coordinate
        normalized_y = smooth_center_y / frame.shape[0]

        return normalized_y, (x, y, w, h)

    return None

while True:
    ret, frame = video_cam.read()
    if ret:
        resized_frame = cv2.resize(frame, TARGET_RESOLUTION)
        result = process_frame(resized_frame)

        if result:
            normalized_y, (x, y, w, h) = result
            
            # Write normalized y-coordinate to JSON file
            with open('face_y.json', 'w') as f:
                print("Normalized y:", normalized_y)
                json.dump({"y": normalized_y}, f)

            # Draw rectangle and circle for visualization
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.circle(frame, (x + w // 2, y + h // 2), 5, (0, 255, 0), -1)

        cv2.imshow('Face Detection', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    time.sleep(0.033)  # Polling rate of 0.1 seconds

video_cam.release()
cv2.destroyAllWindows()
