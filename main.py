import pygame
import cv2
import random
import time

import mediapipe as mp
from mediapipe.tasks.python import vision
from mediapipe.tasks import python
from mediapipe.tasks.python.vision import face_landmarker

from threading import Thread
from queue import Queue

# Initialise MediaPipe face landmarker with the model file
base_options = python.BaseOptions(model_asset_path='face_landmarker.task')
options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    num_faces=1
)
detector = vision.FaceLandmarker.create_from_options(options)

# Start webcam capture
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Convert frame to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    
    # Detect face landmarks
    results = detector.detect(mp_image)
    
    # Extract head position if face found
    if results.face_landmarks:
        face = results.face_landmarks[0]
        nose = face[1]  
        hx = (nose.x - 0.5) * 2
        hy = (nose.y - 0.5) * 2
    
        print(f"Head position: X={hx:.2f}, Y={hy:.2f}")
    
    cv2.imshow('Matrix Perspective Portal', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()