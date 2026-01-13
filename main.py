import pygame
import cv2
import random
import time
import math

import mediapipe as mp
from mediapipe.tasks.python import vision
from mediapipe.tasks import python

from threading import Thread
from queue import Queue

# Import existing components
from matrix_style import MatrixRainSystem
from data_planes import DataPlaneSystem

# Central error display - floating
class CentralErrorDisplay:
    def __init__(self):
        self.pulse_time = 0
        self.pulse_speed = 0.08
        self.glitch_timer = 0
        self.glitch_offset = 0
        
        # 3D position - float in the middle of the tunnel
        self.z_position = 20  # Moved deeper (was 7.5)
        self.x_offset = 0
        self.y_offset = 0
        
        # Subtle float animation
        self.float_time = 0
        self.float_speed = 0.02
        
    def update(self, dt=0.016):
        # Update animations
        self.pulse_time += self.pulse_speed
        self.float_time += self.float_speed
        
        # Random glitch effect
        self.glitch_timer += dt
        if self.glitch_timer > 0.1:
            self.glitch_timer = 0
            self.glitch_offset = random.uniform(-0.2, 0.2) if random.random() < 0.3 else 0
        
        # Subtle floating motion in 3D space
        self.x_offset = math.sin(self.float_time) * 0.3
        self.y_offset = math.cos(self.float_time * 0.7) * 0.2
    
    def render(self, screen, project_func, hx, hy, width, height):
        # Calculate 3D position with float offset
        center_3d_x = self.x_offset + self.glitch_offset
        center_3d_y = self.y_offset
        center_3d_z = self.z_position
        
        # Project to screen space
        center_x, center_y = project_func(center_3d_x, center_3d_y, center_3d_z, hx, hy, width, height)
        
        # Calculate scale based on depth
        z_normalized = (center_3d_z - 0) / (40 - 0)  
        z_normalized = max(0.0, min(1.0, z_normalized))
        depth_scale = 1.0 / (1.0 + z_normalized * 1.5)
        
        # Pulse effect
        pulse_factor = 1.0 + 0.2 * math.sin(self.pulse_time)
        combined_scale = depth_scale * pulse_factor
        
        try:
            font_large = pygame.font.Font(None, int(80 * combined_scale))
            font_small = pygame.font.Font(None, int(40 * combined_scale))
        except:
            return
        
        depth_brightness = 1.0 - (z_normalized * 0.3)
        
        # "SYSTEM" text
        system_color = (int(0 * depth_brightness), int(255 * depth_brightness), int(255 * depth_brightness))
        system_text = font_small.render("SYSTEM", True, system_color)
        system_rect = system_text.get_rect(center=(center_x, center_y - int(40 * combined_scale)))
        screen.blit(system_text, system_rect)
        
        # "ERROR" text 
        error_color = (int(255 * depth_brightness), 0, int(255 * depth_brightness))
        error_text = font_large.render("ERROR", True, error_color)
        error_rect = error_text.get_rect(center=(center_x, center_y + int(20 * combined_scale)))
        
        # Glow effect
        for offset in range(3, 0, -1):
            glow_alpha = 0.2 / offset * depth_brightness
            glow_color = (int(255 * glow_alpha), 0, int(255 * glow_alpha))
            glow_text = font_large.render("ERROR", True, glow_color)
            glow_rect = glow_text.get_rect(center=(center_x, center_y + int(20 * combined_scale)))
            offset_scaled = int(offset * combined_scale)
            screen.blit(glow_text, (glow_rect.x - offset_scaled, glow_rect.y - offset_scaled))
            screen.blit(glow_text, (glow_rect.x + offset_scaled, glow_rect.y + offset_scaled))
        
        screen.blit(error_text, error_rect)
        
        # Warning triangles 
        triangle_size = int(30 * combined_scale)
        triangle_spacing = 4.0  
        
        # Left triangle
        left_x, left_y = project_func(center_3d_x - triangle_spacing, center_3d_y, center_3d_z, hx, hy, width, height)
        self._draw_warning_triangle(screen, left_x, left_y, triangle_size, pulse_factor, depth_brightness)
        
        # Right triangle
        right_x, right_y = project_func(center_3d_x + triangle_spacing, center_3d_y, center_3d_z, hx, hy, width, height)
        self._draw_warning_triangle(screen, right_x, right_y, triangle_size, pulse_factor, depth_brightness)
    
    def _draw_warning_triangle(self, screen, x, y, size, pulse, brightness):
        size = int(size * pulse)
        
        yellow_color = (int(255 * brightness), int(255 * brightness), 0)
        points = [
            (x, y - size),
            (x - size, y + size),
            (x + size, y + size)
        ]
        pygame.draw.polygon(screen, yellow_color, points, max(2, int(3 * pulse)))
        
        pygame.draw.line(screen, yellow_color, (x, y - size//2), (x, y + size//4), max(2, int(3 * pulse)))
        pygame.draw.circle(screen, yellow_color, (x, y + size//2), max(2, int(3 * pulse)))

# Projection constants
SCALE = 120
EYE_DIST = 8.0

def project(x, y, z, hx, hy, width, height):
    d = EYE_DIST + z
    if d <= 0:
        d = 0.01
    f = EYE_DIST / d
    sx = hx + (x - hx) * f
    sy = hy + (y - hy) * f
    px = int(width/2 + sx * SCALE)
    py = int(height/2 + sy * SCALE)
    return px, py

def get_head_position(cap, detector):
    # Get head position using MediaPipe Face Landmarker
    ret, frame = cap.read()
    if not ret:
        return 0, 0, False
    
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    
    results = detector.detect(mp_image)
    
    if not results.face_landmarks:
        return 0, 0, False
    
    # Use nose tip 
    nose = results.face_landmarks[0][1]
    hx = (nose.x - 0.5) * 2
    hy = (nose.y - 0.5) * 2
    
    return hx, hy, True

# Initialise MediaPipe Face Landmarker
base_options = python.BaseOptions(model_asset_path='face_landmarker.task')
options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    num_faces=1
)
detector = vision.FaceLandmarker.create_from_options(options)

# Initialise pygame
pygame.init()

WINDOWED = True 
WINDOW_WIDTH = 1280  
WINDOW_HEIGHT = 720

if WINDOWED:
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
else:
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

WIN_WIDTH, WIN_HEIGHT = screen.get_size()
pygame.display.set_caption("SYSTEM ERROR - Cyberpunk Portal")
clock = pygame.time.Clock()

# Calculate bounds
aspect_ratio = WIN_WIDTH / WIN_HEIGHT
y_range = 12
x_range = y_range * aspect_ratio

min_x = -x_range / 2
max_x = x_range / 2
min_y = -6
max_y = 6
min_z = 0
max_z = 40  

bounds = (min_x, max_x, min_y, max_y, min_z, max_z)

# Create systems with CYBERPUNK COLORS
rain_system = MatrixRainSystem(num_streams=400, bounds=bounds)
plane_system = DataPlaneSystem(num_planes=25, bounds=bounds) 

# Create central error display
central_display = CentralErrorDisplay()

# Start webcam
cap = cv2.VideoCapture(0)

# Head position smoothing
prev_hx, prev_hy = 0.0, 0.0
SMOOTHING_FACTOR = 0.7

# Base bounds
BASE_Y_RANGE = 12
BASE_ASPECT_RATIO = WIN_WIDTH / WIN_HEIGHT

# Glitch effect variables
glitch_intensity = 0
glitch_timer = 0

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        if event.type == pygame.VIDEORESIZE:
            # Handle window resize
            WIN_WIDTH, WIN_HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT), pygame.RESIZABLE)
            
            # Recalculate bounds for new aspect ratio
            aspect_ratio = WIN_WIDTH / WIN_HEIGHT
            y_range = 12
            x_range = y_range * aspect_ratio
            min_x = -x_range / 2
            max_x = x_range / 2
            dynamic_bounds = (min_x, max_x, -6, 6, 0, 40)
            
            plane_system.update_bounds(dynamic_bounds)
            rain_system.update_bounds(dynamic_bounds)
    
    # Get head position
    hx, hy, ok = get_head_position(cap, detector)
    
    if ok:
        # Apply smoothing
        hx = prev_hx * SMOOTHING_FACTOR + hx * (1 - SMOOTHING_FACTOR)
        hy = prev_hy * SMOOTHING_FACTOR + hy * (1 - SMOOTHING_FACTOR)
        prev_hx, prev_hy = hx, hy
    else:
        hx, hy = 0, 0
    
    # Clear screen with dark background
    screen.fill((5, 0, 10)) 
    
    # Scale head position
    hx_scaled = hx * 8
    hy_scaled = hy * 8
    
    # Calculate dynamic bounds
    dynamic_bounds = (-x_range/2, x_range/2, -y_range/2, y_range/2, 0, 40)  
    
    # Update bounds
    plane_system.update_bounds(dynamic_bounds)
    rain_system.update_bounds(dynamic_bounds)
    
    # Update all systems
    dt = 1/60
    rain_system.update()
    plane_system.update()
    central_display.update(dt)
    
    # Glitch effect disabled
    glitch_intensity = 0
    
    # No glitch offset to head position
    hx_glitched = hx_scaled
    hy_glitched = hy_scaled
    
    # Render in depth order
    plane_system.render(screen, project, hx_glitched, hy_glitched, WIN_WIDTH, WIN_HEIGHT)
    rain_system.render(screen, project, hx_glitched, hy_glitched, WIN_WIDTH, WIN_HEIGHT)
    
    # Render central error display 
    central_display.render(screen, project, hx_glitched, hy_glitched, WIN_WIDTH, WIN_HEIGHT)
    
    # Scan Lines
    if random.random() < 0.3:
        scan_y = random.randint(0, WIN_HEIGHT)
        pygame.draw.line(screen, (0, 100, 100), (0, scan_y), (WIN_WIDTH, scan_y), 1)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
cap.release()