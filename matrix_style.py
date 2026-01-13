import pygame
import random

class MatrixStream:
    CHARS = list("ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ0123456789ABCDEFZ!?")
    
    def __init__(self, start_point, end_point, trail_length=12, color='cyan'):
        self.start_point = start_point
        self.end_point = end_point
        self.trail_length = trail_length
        
        if color == 'cyan':
            self.base_color = (0, 255, 255)
        elif color == 'magenta':
            self.base_color = (255, 0, 255)
        elif color == 'yellow':
            self.base_color = (255, 255, 0)
        else:
            choice = random.choice(['cyan', 'magenta', 'yellow'])
            if choice == 'cyan':
                self.base_color = (0, 255, 255)
            elif choice == 'magenta':
                self.base_color = (255, 0, 255)
            else:
                self.base_color = (255, 255, 0)
        
        self.progress = random.uniform(-0.3, 0.0)
        self.speed = random.uniform(0.008, 0.015)
        self.char_spacing = 0.06
        self.char_change_probability = random.uniform(0.02, 0.05)
        
        self.characters = []
        for i in range(trail_length):
            self.characters.append({
                'char': random.choice(self.CHARS),
                'brightness': self._calculate_brightness(i)
            })
    
    def _calculate_brightness(self, index):
        if index == 0:
            return 255
        else:
            fade = 1.0 - (index / self.trail_length)
            return int(50 + (fade * 150))
    
    def _interpolate_point(self, t):
        t = max(0.0, min(1.0, t))
        sx, sy, sz = self.start_point
        ex, ey, ez = self.end_point
        
        x = sx + (ex - sx) * t
        y = sy + (ey - sy) * t
        z = sz + (ez - sz) * t
        
        return (x, y, z)
    
    def update(self):
        self.progress += self.speed
        
        for i, char_data in enumerate(self.characters):
            change_prob = self.char_change_probability * (1 + i * 0.3)
            if random.random() < change_prob:
                char_data['char'] = random.choice(self.CHARS)
    
    def reset(self):
        self.progress = -0.3
        self.speed = random.uniform(0.008, 0.015)
        self.char_change_probability = random.uniform(0.02, 0.05)
        
        for i, char_data in enumerate(self.characters):
            char_data['char'] = random.choice(self.CHARS)
            char_data['brightness'] = self._calculate_brightness(i)
    
    def get_characters(self):
        characters = []
        
        for i in range(self.trail_length):
            char_progress = self.progress - (i * self.char_spacing)
            
            if char_progress < 0 or char_progress > 1.2:
                continue
            
            x, y, z = self._interpolate_point(char_progress)
            
            char_data = self.characters[i]
            characters.append((x, y, z, char_data['char'], char_data['brightness']))
        
        return characters
    
    def is_finished(self):
        return self.progress > 1.3
    
    def get_base_color(self):
        return self.base_color


class MatrixRainSystem:
    BASE_FONT_SIZE = 20
    NEAR_Z = 0.0
    FAR_Z = 15.0
    MIN_FONT_SIZE = 8
    MAX_FONT_SIZE = 60
    
    def __init__(self, num_streams=400, bounds=(-10, 10, -8, 8, 0, 15), color='random'):
        self.bounds = bounds
        self.num_streams = num_streams
        self.color_mode = color
        self._init_streams()
        
        self.font_cache = {}
        self._init_font_cache()
    
    def _init_streams(self):
        """Initialize streams with cyberpunk colors"""
        self.streams = []
        min_x, max_x, min_y, max_y, min_z, max_z = self.bounds
        
        color_pool = ['cyan'] * 40 + ['magenta'] * 35 + ['yellow'] * 25
        
        # Floor streams
        for _ in range(int(self.num_streams * 0.4)):
            x = random.uniform(min_x, max_x)
            start = (x, min_y, min_z)
            end = (x, min_y, max_z)
            trail_length = random.randint(10, 18)
            color = random.choice(color_pool) if self.color_mode == 'random' else self.color_mode
            self.streams.append(MatrixStream(start, end, trail_length, color))
        
        # Ceiling streams
        for _ in range(int(self.num_streams * 0.4)):
            x = random.uniform(min_x, max_x)
            start = (x, max_y, min_z)
            end = (x, max_y, max_z)
            trail_length = random.randint(10, 18)
            color = random.choice(color_pool) if self.color_mode == 'random' else self.color_mode
            self.streams.append(MatrixStream(start, end, trail_length, color))
        
        # Left wall streams
        for _ in range(int(self.num_streams * 0.1)):
            y = random.uniform(min_y, max_y)
            start = (min_x, y, min_z)
            end = (min_x, y, max_z)
            trail_length = random.randint(10, 18)
            color = random.choice(color_pool) if self.color_mode == 'random' else self.color_mode
            self.streams.append(MatrixStream(start, end, trail_length, color))
        
        # Right wall streams
        for _ in range(int(self.num_streams * 0.1)):
            y = random.uniform(min_y, max_y)
            start = (max_x, y, min_z)
            end = (max_x, y, max_z)
            trail_length = random.randint(10, 18)
            color = random.choice(color_pool) if self.color_mode == 'random' else self.color_mode
            self.streams.append(MatrixStream(start, end, trail_length, color))
        
        self.streams.sort(key=lambda s: (s.start_point[2] + s.end_point[2]) / 2, reverse=True)
    
    def update_bounds(self, new_bounds):
        old_bounds = self.bounds
        self.bounds = new_bounds
        
        old_x_range = old_bounds[1] - old_bounds[0]
        old_y_range = old_bounds[3] - old_bounds[2]
        new_x_range = new_bounds[1] - new_bounds[0]
        new_y_range = new_bounds[3] - new_bounds[2]
        
        x_change = abs(new_x_range - old_x_range) / old_x_range if old_x_range > 0 else 1
        y_change = abs(new_y_range - old_y_range) / old_y_range if old_y_range > 0 else 1
        
        if x_change > 0.2 or y_change > 0.2:
            self._init_streams()
    
    def _init_font_cache(self):
        font_path = None
        
        try:
            font_path = '/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc'
            test_font = pygame.font.Font(font_path, 20)
        except:
            try:
                font_path = 'hiragino sans'
                test_font = pygame.font.SysFont(font_path, 20)
            except:
                font_path = None
        
        for size in range(self.MIN_FONT_SIZE, self.MAX_FONT_SIZE + 1, 2):
            try:
                if font_path and font_path.endswith('.ttc'):
                    self.font_cache[size] = pygame.font.Font(font_path, size)
                elif font_path:
                    self.font_cache[size] = pygame.font.SysFont(font_path, size)
                else:
                    self.font_cache[size] = pygame.font.Font(None, size)
            except:
                self.font_cache[size] = pygame.font.Font(None, size)
    
    def _get_font_for_size(self, size):
        clamped_size = max(self.MIN_FONT_SIZE, min(self.MAX_FONT_SIZE, size))
        rounded_size = round(clamped_size / 2) * 2
        
        if rounded_size not in self.font_cache:
            rounded_size = self.BASE_FONT_SIZE
        
        return self.font_cache[rounded_size]
    
    def _calculate_scale_factor(self, z):
        z_normalized = (z - self.NEAR_Z) / (self.FAR_Z - self.NEAR_Z)
        z_normalized = max(0.0, min(1.0, z_normalized))
        scale_factor = 1.0 / (1.0 + z_normalized * 2.0)
        return scale_factor
    
    def _calculate_depth_brightness(self, base_brightness, z):
        z_normalized = (z - self.NEAR_Z) / (self.FAR_Z - self.NEAR_Z)
        z_normalized = max(0.0, min(1.0, z_normalized))
        depth_fade = 1.0 - (z_normalized * 0.5)
        return int(base_brightness * depth_fade)
    
    def update(self):
        for stream in self.streams:
            stream.update()
            if stream.is_finished():
                stream.reset()
    
    def render(self, screen, project_func, hx, hy, width, height):
        for stream in self.streams:
            base_color = stream.get_base_color()
            
            for x, y, z, char, brightness in stream.get_characters():
                px, py = project_func(x, y, z, hx, hy, width, height)
                
                if px < -50 or px > width + 50 or py < -50 or py > height + 50:
                    continue
                
                scale_factor = self._calculate_scale_factor(z)
                font_size = int(self.BASE_FONT_SIZE * scale_factor)
                font = self._get_font_for_size(font_size)
                
                final_brightness = self._calculate_depth_brightness(brightness, z)
                
                r, g, b = base_color
                colour = (
                    int(r * final_brightness / 255),
                    int(g * final_brightness / 255),
                    int(b * final_brightness / 255)
                )
                
                try:
                    text_surface = font.render(char, True, colour)
                    char_rect = text_surface.get_rect(center=(px, py))
                    screen.blit(text_surface, char_rect)
                except:
                    pass