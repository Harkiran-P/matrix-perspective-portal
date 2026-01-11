import pygame
import random

# A vertical column of falling Matrix characters.
class MatrixColumn:
    CHARS = list("ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ0123456789ABCDEFZ")
    
    def __init__(self, x, z, trail_length=8):
        # Initialize a column at fixed 3D position (x, z) with a trail of characters.
        # trail_length: how many characters form the falling stream (head + tail)
        self.x = x
        self.z = z
        self.trail_length = trail_length
        
        self.characters = []
        self.head_y = random.uniform(-10, 0)  
        self.speed = random.uniform(0.08, 0.18)
        self.char_spacing = 0.5
        
        # Initialise the trail of characters behind the head
        for i in range(trail_length):
            char = random.choice(self.CHARS)
            y_pos = self.head_y - (i * self.char_spacing)
            brightness = self._calculate_brightness(i)
            self.characters.append({
                'char': char,
                'y': y_pos,
                'brightness': brightness
            })
    
    def _calculate_brightness(self, index):
        # Calculate brightness based on position in trail. Index 0 = head (brightest white)
        if index == 0:
            return 255  # Bright white/green head
        else:
            # Fade from bright (200) to dark (50) along the trail
            fade = 1.0 - (index / self.trail_length)
            return int(50 + (fade * 150))
    
    def update(self):
        # Move the entire column down by updating head position.
        self.head_y += self.speed
        
        # Update each character's Y position relative to head
        for i, char_data in enumerate(self.characters):
            char_data['y'] = self.head_y - (i * self.char_spacing)
            
            # Randomly change character to create matrixy(??) effect
            if random.random() < 0.03:
                char_data['char'] = random.choice(self.CHARS)
        
    def reset(self, y_min):

        self.head_y = y_min - 2  
        self.speed = random.uniform(0.08, 0.18)
        
        # Regenerate all characters in the trail
        for i, char_data in enumerate(self.characters):
            char_data['char'] = random.choice(self.CHARS)
            char_data['y'] = self.head_y - (i * self.char_spacing)
            char_data['brightness'] = self._calculate_brightness(i)
    
    def get_characters(self):
        # Return list of tuples for rendering: (x, y, z, char, brightness)

        return [(self.x, char_data['y'], self.z, 
                 char_data['char'], char_data['brightness']) 
                for char_data in self.characters]


class MatrixRainSystem:
    #Handles spawning, updating, and rendering the entire rain effect.
    
    def __init__(self, num_columns=40, bounds=(-10, 10, -8, 8, 0, 15)):
        self.bounds = bounds
        self.columns = []
        
        min_x, max_x, min_y, max_y, min_z, max_z = bounds
        
        # Spawn columns at random X/Z positions with varying trail lengths
        for _ in range(num_columns):
            x = random.uniform(min_x, max_x)
            z = random.uniform(min_z, max_z)
            trail_length = random.randint(6, 12)  
            self.columns.append(MatrixColumn(x, z, trail_length))
        
        try:
            self.font = pygame.font.Font('/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc', 20)
        except:
            try:
                self.font = pygame.font.SysFont('hiragino sans', 20)
            except:
                self.font = pygame.font.Font(None, 20)
    
    def update(self):
        # Update all columns each frame.

        min_x, max_x, min_y, max_y, min_z, max_z = self.bounds
        
        for column in self.columns:
            column.update()
            if column.head_y > max_y + 2:
                column.reset(min_y)
    
    def render(self, screen, project_func, hx, hy, width, height):
        #Render all characters from all columns using 3D projection.

        for column in self.columns:
            # Get all characters in this column
            for x, y, z, char, brightness in column.get_characters():

                # Project 3D position to 2D screen coordinates
                px, py = project_func(x, y, z, hx, hy, width, height)
                
                # Skip characters that are off-screen (optimisation)
                if px < 0 or px > width or py < 0 or py > height:
                    continue
                
                # Render character with brightness-based green colour
                colour = (0, brightness, 0)
                text_surface = self.font.render(char, True, colour)
                screen.blit(text_surface, (px, py))