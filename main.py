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

# Projection constants
SCALE = 120
EYE_DIST = 8.0

def project(x, y, z, hx, hy, width, height):
    """
    Projects a 3D point onto 2D screen based on head position.
    Creates the off-axis perspective illusion.
    """
    d = EYE_DIST + z
    f = EYE_DIST / d
    sx = hx + (x - hx) * f
    sy = hy + (y - hy) * f
    px = int(width/2 + sx * SCALE)
    py = int(height/2 + sy * SCALE)
    return px, py

# Initialise MediaPipe face landmarker with the model file
base_options = python.BaseOptions(model_asset_path='face_landmarker.task')
options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    num_faces=1
)
detector = vision.FaceLandmarker.create_from_options(options)

# Initialise pygame window for 3D rendering (fullscreen)
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIN_WIDTH, WIN_HEIGHT = screen.get_size()
pygame.display.set_caption("Matrix Perspective Portal")
clock = pygame.time.Clock()

# Start webcam capture
cap = cv2.VideoCapture(0)

running = True
while running:
    # Handle pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
    
    ret, frame = cap.read()
    if not ret:
        break
    
    # Convert frame to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    
    # Detect face landmarks
    results = detector.detect(mp_image)
    
    # Extract head position if face found (default to centre if no face)
    hx, hy = 0, 0
    if results.face_landmarks:
        face = results.face_landmarks[0]
        nose = face[1]  
        hx = (nose.x - 0.5) * 2
        hy = (nose.y - 0.5) * 2
    
    # Clear pygame screen (black background)
    screen.fill((0, 0, 0))
    
    # Scale head position for more dramatic effect
    hx_scaled = hx * 5
    hy_scaled = hy * 5
    
    # Define a larger 3D box that fills more of the screen
    box_front = [
        (-8, -6, 0),   # top-left front
        (8, -6, 0),    # top-right front
        (8, 6, 0),     # bottom-right front
        (-8, 6, 0)     # bottom-left front
    ]
    
    box_back = [
        (-8, -6, 10),   # top-left back (deeper too)
        (8, -6, 10),    # top-right back
        (8, 6, 10),     # bottom-right back
        (-8, 6, 10)     # bottom-left back
    ]
    
    # Project all 3D points to 2D screen coordinates
    front_projected = [project(x, y, z, hx_scaled, hy_scaled, WIN_WIDTH, WIN_HEIGHT) 
                       for x, y, z in box_front]
    back_projected = [project(x, y, z, hx_scaled, hy_scaled, WIN_WIDTH, WIN_HEIGHT) 
                      for x, y, z in box_back]
    
    # Draw the front face (green)
    pygame.draw.lines(screen, (0, 255, 0), True, front_projected, 2)
    
    # Draw the back face (green)
    pygame.draw.lines(screen, (0, 255, 0), True, back_projected, 2)
    
    # Draw connecting lines between front and back
    for i in range(4):
        pygame.draw.line(screen, (0, 255, 0), front_projected[i], back_projected[i], 2)
    
    # Update displays
    pygame.display.flip()
    cv2.imshow('Camera Feed', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        running = False
    
    clock.tick(60)  # 60 FPS cap

pygame.quit()
cap.release()
cv2.destroyAllWindows()