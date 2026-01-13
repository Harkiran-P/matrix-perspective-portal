import pygame
import random
import math
import time

class DataPlane:
    """A single data plane - a wireframe rectangle with error messages"""
    
    ERROR_MESSAGES = [
        "CRITICAL ERROR",
        "ACCESS DENIED",
        "SYSTEM FAILURE",
        "DATA CORRUPT",
        "CONNECTION LOST",
        "BREACH DETECTED",
        "WARNING",
        "ALERT",
        "FIREWALL DOWN",
        "UNAUTHORIZED",
        "TIMEOUT",
        "FATAL ERROR",
        "!",
        "!!",
        "ERROR CODE: 0x8F4A",
        "BUFFER OVERFLOW",
        "STACK TRACE",
        "SEGFAULT",
        "CORE DUMPED"
    ]
    
    def __init__(self, z_depth, width, height):
        self.z = z_depth
        self.width = width
        self.height = height
        
        self.corners = [
            (-width/2, -height/2, z_depth),  # Bottom-left
            (width/2, -height/2, z_depth),   # Bottom-right
            (width/2, height/2, z_depth),    # Top-right
            (-width/2, height/2, z_depth)    # Top-left
        ]
        
        # Generate error messages scattered across the plane
        self.messages = []
        num_messages = random.randint(5, 10)
        for _ in range(num_messages):
            x = random.uniform(-width/2 + 0.5, width/2 - 0.5)
            y = random.uniform(-height/2 + 0.5, height/2 - 0.5)
            msg = random.choice(self.ERROR_MESSAGES)
            
            color_choice = random.choice(['cyan', 'magenta', 'yellow'])
            if color_choice == 'cyan':
                color = (0, 255, 255)
            elif color_choice == 'magenta':
                color = (255, 0, 255)
            else:
                color = (255, 255, 0)
            
            brightness = random.uniform(0.5, 1.0)
            self.messages.append({
                'pos': (x, y, z_depth),
                'text': msg,
                'color': color,
                'brightness': brightness,
                'change_timer': random.randint(60, 180),
                'glitch_timer': 0,
                'glitch_offset': 0
            })
        
        self.frame_color_time = random.uniform(0, math.pi * 2)
        self.frame_color_speed = 0.05
        
        # Pulsing effect
        self.pulse_offset = random.uniform(0, math.pi * 2)
        self.pulse_speed = random.uniform(0.03, 0.06)
        self.pulse_time = 0
        
    def update(self):
        # Update animations
        self.pulse_time += self.pulse_speed
        self.frame_color_time += self.frame_color_speed
        
        # Update messages
        for msg in self.messages:
            msg['change_timer'] -= 1
            if msg['change_timer'] <= 0:
                msg['text'] = random.choice(self.ERROR_MESSAGES)
                msg['change_timer'] = random.randint(60, 180)
            
            # Glitch effect
            msg['glitch_timer'] += 0.016
            if msg['glitch_timer'] > 0.1:
                msg['glitch_timer'] = 0
                msg['glitch_offset'] = random.uniform(-3, 3) if random.random() < 0.2 else 0
    
    def _calculate_depth_alpha(self, z, min_z=0, max_z=40):
        # Calculate brightness based on depth 
        z_normalized = (z - min_z) / (max_z - min_z)
        z_normalized = max(0.0, min(1.0, z_normalized))
        
        # Exponential fade 
        alpha = math.exp(-z_normalized * 2.5)  
        return alpha
    
    def _get_frame_color(self):
        factor = (math.sin(self.frame_color_time) + 1) / 2
        
        cyan = (0, 255, 255)
        magenta = (255, 0, 255)
        
        r = int(cyan[0] * (1 - factor) + magenta[0] * factor)
        g = int(cyan[1] * (1 - factor) + magenta[1] * factor)
        b = int(cyan[2] * (1 - factor) + magenta[2] * factor)
        
        return (r, g, b)
    
    def render(self, screen, project_func, hx, hy, width, height):
        # Render the data plane with wireframe and error messages
        
        pulse_factor = 1.0 + 0.3 * math.sin(self.pulse_time + self.pulse_offset)
        
        base_alpha = self._calculate_depth_alpha(self.z)
        alpha = base_alpha * pulse_factor
        
        if alpha < 0.05:
            return
        
        projected_corners = []
        for corner in self.corners:
            try:
                px, py = project_func(*corner, hx, hy, width, height)
                projected_corners.append((px, py))
            except:
                return
        
        # Get frame color
        frame_base_color = self._get_frame_color()
        r, g, b = frame_base_color
        frame_color = (int(r * alpha), int(g * alpha), int(b * alpha))
        
        # Draw wireframe edges with glow
        for i in range(4):
            p1 = projected_corners[i]
            p2 = projected_corners[(i + 1) % 4]
            
            try:
                for thickness, glow_mult in [(6, 0.2), (4, 0.4)]:
                    glow_alpha = alpha * glow_mult
                    glow_color = (int(r * glow_alpha), int(g * glow_alpha), int(b * glow_alpha))
                    pygame.draw.line(screen, glow_color, p1, p2, thickness)

                pygame.draw.line(screen, frame_color, p1, p2, 2)
            except:
                pass
        
        # Render error messages
        self._render_messages(screen, project_func, hx, hy, width, height, base_alpha)
    
    def _render_messages(self, screen, project_func, hx, hy, width, height, base_alpha):
        # Render error messages on the plane surface
        
        z_normalized = (self.z - 0) / (40 - 0)
        z_normalized = max(0.0, min(1.0, z_normalized))
        scale_factor = 1.0 / (1.0 + z_normalized * 2.0)
        font_size = int(20 * scale_factor)
        font_size = max(8, min(36, font_size))
        
        try:
            font = pygame.font.Font(None, font_size)
        except:
            return
        
        for msg in self.messages:
            pos = msg['pos']
            text = msg['text']
            color = msg['color']
            brightness = msg['brightness']
            glitch_offset = msg['glitch_offset']
            
            try:
                px, py = project_func(*pos, hx, hy, width, height)
                px += glitch_offset
            except:
                continue
            
            if px < -100 or px > width + 100 or py < -100 or py > height + 100:
                continue
            
            # Calculate final color with depth and brightness
            final_alpha = base_alpha * brightness
            r, g, b = color
            text_color = (int(r * final_alpha), int(g * final_alpha), int(b * final_alpha))
            
            # Render with glow
            try:
                glow_color = (int(r * final_alpha * 0.3), int(g * final_alpha * 0.3), int(b * final_alpha * 0.3))
                for ox, oy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
                    glow_surface = font.render(text, True, glow_color)
                    glow_rect = glow_surface.get_rect(center=(px + ox*2, py + oy*2))
                    screen.blit(glow_surface, glow_rect)
                
                text_surface = font.render(text, True, text_color)
                text_rect = text_surface.get_rect(center=(px, py))
                screen.blit(text_surface, text_rect)
            except:
                pass


class DataPlaneSystem:
    # Manages multiple data planes at different depths
    
    def __init__(self, num_planes=25, bounds=(-10, 10, -8, 8, 0, 40)):
        self.bounds = bounds
        self.num_planes = num_planes
        self.planes = []
        self._init_planes()
        self._init_longitudinal_lines()
    
    def _init_longitudinal_lines(self):
        # Create longitudinal lines 
        min_x, max_x, min_y, max_y, min_z, max_z = self.bounds
        
        self.longitudinal_lines = []
        
        plane_width = (max_x - min_x) * 0.95
        plane_height = (max_y - min_y) * 0.95
        
        corners_2d = [
            (-plane_width/2, -plane_height/2),  # Bottom-left
            (plane_width/2, -plane_height/2),   # Bottom-right
            (plane_width/2, plane_height/2),    # Top-right
            (-plane_width/2, plane_height/2)    # Top-left
        ]
        
        for x, y in corners_2d:
            self.longitudinal_lines.append({
                'start': (x, y, min_z),
                'end': (x, y, max_z),
                'type': 'corner'
            })
        
        num_h_lines = 8  # Horizontal divisions
        num_v_lines = 6  # Vertical divisions
        
        # Horizontal longitudinal lines
        for i in range(1, num_h_lines):
            y = -plane_height/2 + (i / num_h_lines) * plane_height
            # Left edge
            self.longitudinal_lines.append({
                'start': (-plane_width/2, y, min_z),
                'end': (-plane_width/2, y, max_z),
                'type': 'grid'
            })
            # Right edge
            self.longitudinal_lines.append({
                'start': (plane_width/2, y, min_z),
                'end': (plane_width/2, y, max_z),
                'type': 'grid'
            })
        
        # Vertical longitudinal lines
        for i in range(1, num_v_lines):
            x = -plane_width/2 + (i / num_v_lines) * plane_width
            # Top edge
            self.longitudinal_lines.append({
                'start': (x, -plane_height/2, min_z),
                'end': (x, -plane_height/2, max_z),
                'type': 'grid'
            })
            # Bottom edge
            self.longitudinal_lines.append({
                'start': (x, plane_height/2, min_z),
                'end': (x, plane_height/2, max_z),
                'type': 'grid'
            })
    
    def get_farthest_plane_dimensions(self):
        # Get the dimensions of the smallest plane
        if self.planes:
            farthest = max(self.planes, key=lambda p: p.z)
            return farthest.width, farthest.height
        return None, None
    
    def _init_planes(self):
        # Create planes at evenly spaced depths
        min_x, max_x, min_y, max_y, min_z, max_z = self.bounds
        
        self.planes = []
        
        depth_step = (max_z - min_z) / (self.num_planes + 1)
        
        for i in range(self.num_planes):
            z = min_z + depth_step * (i + 1)
            
            # Full size planes
            plane_width = (max_x - min_x) * 0.95
            plane_height = (max_y - min_y) * 0.95
            
            plane = DataPlane(z, plane_width, plane_height)
            self.planes.append(plane)
        
        # Sort by depth (far to near)
        self.planes.sort(key=lambda p: p.z, reverse=True)
    
    def update_bounds(self, new_bounds):
        # Update bounds and reinitialise planes if needed
        old_bounds = self.bounds
        self.bounds = new_bounds
        
        old_x_range = old_bounds[1] - old_bounds[0]
        old_y_range = old_bounds[3] - old_bounds[2]
        new_x_range = new_bounds[1] - new_bounds[0]
        new_y_range = new_bounds[3] - new_bounds[2]
        
        x_change = abs(new_x_range - old_x_range) / old_x_range if old_x_range > 0 else 1
        y_change = abs(new_y_range - old_y_range) / old_y_range if old_y_range > 0 else 1
        
        if x_change > 0.2 or y_change > 0.2:
            self._init_planes()
            self._init_longitudinal_lines()
    
    def update(self):
        # Update all planes
        for plane in self.planes:
            plane.update()
    
    def render(self, screen, project_func, hx, hy, width, height):
        # Render all planes and longitudinal lines in depth order
        
        self._render_longitudinal_lines(screen, project_func, hx, hy, width, height)
        
        for plane in self.planes:
            plane.render(screen, project_func, hx, hy, width, height)
    
    def _render_longitudinal_lines(self, screen, project_func, hx, hy, width, height):
        # Render the longitudinal corner lines with depth-based fading
        
        for line_data in self.longitudinal_lines:
            start_3d = line_data['start']
            end_3d = line_data['end']
            line_type = line_data['type']
            
            try:
                start_2d = project_func(*start_3d, hx, hy, width, height)
                end_2d = project_func(*end_3d, hx, hy, width, height)
            except:
                continue
            
            # Draw in segments for smooth depth fading
            min_z, max_z = self.bounds[4], self.bounds[5]
            num_segments = 40
            
            # Different alpha multipliers for different line types
            if line_type == 'corner':
                alpha_multiplier = 1.0  
                thickness_main = 2
                thickness_glow = 4
            else:  
                alpha_multiplier = 0.85 
                thickness_main = 1
                thickness_glow = 2
            
            for i in range(num_segments):
                z1 = min_z + (i / num_segments) * (max_z - min_z)
                z2 = min_z + ((i + 1) / num_segments) * (max_z - min_z)
                
                # Calculate alpha for this segment
                avg_z = (z1 + z2) / 2
                z_normalized = (avg_z - min_z) / (max_z - min_z)
                alpha = math.exp(-z_normalized * 2.5) * alpha_multiplier
                
                if alpha < 0.02:  
                    continue
                
                # Interpolate points along the line
                t1 = i / num_segments
                t2 = (i + 1) / num_segments
                
                p1 = (
                    int(start_2d[0] + t1 * (end_2d[0] - start_2d[0])),
                    int(start_2d[1] + t1 * (end_2d[1] - start_2d[1]))
                )
                p2 = (
                    int(start_2d[0] + t2 * (end_2d[0] - start_2d[0])),
                    int(start_2d[1] + t2 * (end_2d[1] - start_2d[1]))
                )
                
                color_time = time.time() * 0.5
                factor = (math.sin(color_time) + 1) / 2
                
                cyan = (0, 255, 255)
                magenta = (255, 0, 255)
                
                r = int((cyan[0] * (1 - factor) + magenta[0] * factor) * alpha)
                g = int((cyan[1] * (1 - factor) + magenta[1] * factor) * alpha)
                b = int((cyan[2] * (1 - factor) + magenta[2] * factor) * alpha)
                
                line_color = (r, g, b)
                
                try:
                    glow_color = (int(r * 0.4), int(g * 0.4), int(b * 0.4))
                    pygame.draw.line(screen, glow_color, p1, p2, thickness_glow)
                    pygame.draw.line(screen, line_color, p1, p2, thickness_main)
                except:
                    pass