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

# Other file imports
from matrix_style import MatrixRainSystem

# Projection constants for converting 3D coordinates to 2D screen space
SCALE = 120
EYE_DIST = 8.0

# Projects a 3D point (x, y, z) onto 2D screen coordinates based on head position.
# Creates the off-axis perspective illusion - objects closer to viewer appear to move more.
def project(x, y, z, hx, hy, width, height):
    d = EYE_DIST + z
    f = EYE_DIST / d
    sx = hx + (x - hx) * f
    sy = hy + (y - hy) * f
    px = int(width/2 + sx * SCALE)
    py = int(height/2 + sy * SCALE)
    return px, py

# Initialise MediaPipe face detector with the pre-trained model
base_options = python.BaseOptions(model_asset_path='face_landmarker.task')
options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    num_faces=1
)
detector = vision.FaceLandmarker.create_from_options(options)

# Initialise pygame fullscreen window and get display dimensions
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIN_WIDTH, WIN_HEIGHT = screen.get_size()
pygame.display.set_caption("Matrix Perspective Portal")
clock = pygame.time.Clock()

# Create the Matrix rain system with 40 columns spread across 3D space
rain_system = MatrixRainSystem(num_columns=45, bounds=(-10, 10, -8, 8, 0, 15))

# Start webcam capture for head tracking
cap = cv2.VideoCapture(0)

# Main rendering loop
running = True
while running:
    # Handle user input events (quit on q key)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
    
    # Capture frame from webcam and convert to RGB for MediaPipe
    ret, frame = cap.read()
    if not ret:
        break
    
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    
    # Detect face landmarks and extract nose position for head tracking
    results = detector.detect(mp_image)
    
    hx, hy = 0, 0
    if results.face_landmarks:
        face = results.face_landmarks[0]
        nose = face[1]  
        hx = (nose.x - 0.5) * 2  # Normalize to -1 to +1 range
        hy = (nose.y - 0.5) * 2
    
    # Clear screen with black background
    screen.fill((0, 0, 0))
    
    # Scale head position for more dramatic parallax effect
    hx_scaled = hx * 5
    hy_scaled = hy * 5
    
    # Update rain physics and render all columns to screen
    rain_system.update()
    rain_system.render(screen, project, hx_scaled, hy_scaled, WIN_WIDTH, WIN_HEIGHT)
    
    # Update both pygame display and OpenCV camera preview window
    pygame.display.flip()
    cv2.imshow('Camera Feed', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        running = False
    
    clock.tick(60)  # Maintain 60 FPS

# Clean up resources on exit
pygame.quit()
cap.release()
cv2.destroyAllWindows()