# SYSTEM ERROR - Cyberpunk Portal

A 3D cyberpunk visualisation that responds to your head movements in real-time, creating an immersive tunnel effect with Matrix-style code rain, floating error messages, and dynamic data planes.

## Features

- **Head Tracking**: Uses your webcam and MediaPipe to track head movements, creating a parallax 3D effect
- **Matrix Rain**: Cascading Japanese katakana characters reminiscent of the matrix but in cyberpunk colors (cyan, magenta, yellow)
- **Data Planes**: Floating wireframe rectangles with glitching error messages
- **Central Error Display**: A pulsing "SYSTEM ERROR" message that floats in 3D space
- **Dynamic Depth**: All elements fade naturally based on their distance from the viewer
- **Resizable Window**: Automatically adjusts to window size changes
- **Smooth Animations**: 60 FPS rendering with pulsing effects and glitch aesthetics

## Requirements

- Python 3.7+
- Webcam

## Installation

1. Clone this repository:
```bash
git clone https://github.com/Harkiran-P/cyberpunk-portal.git
cd cyberpunk-portal
```

2. Install required packages:
```bash
pip install pygame opencv-python mediapipe
```

3. Download the MediaPipe Face Landmarker model:
   - Download `face_landmarker.task` from [MediaPipe's models](https://developers.google.com/mediapipe/solutions/vision/face_landmarker#models)
   - Place it in the project root directory

## Usage

Run the main script:
```bash
python3 main.py
```

**Controls:**
- Move your head to look around the 3D tunnel
- Press `ESC` to exit
- Resize the window to adjust the viewport

## Project Structure

```
cyberpunk-portal/
├── main.py              # Main application and rendering loop
├── matrix_style.py      # Matrix rain effect system
├── data_planes.py       # Floating data plane system
├── face_landmarker.task # MediaPipe model (not included)
└── README.md
```

## How It Works

### Head Tracking
The application uses MediaPipe's Face Landmarker to detect your nose position in real-time. This position is mapped to a 3D viewport coordinate, creating a parallax effect where elements shift based on your perspective.

### 3D Projection
All elements exist in 3D space (x, y, z coordinates) and are projected onto the 2D screen using perspective projection. Objects farther away appear smaller and dimmer, creating depth.

### Visual Elements

- **Matrix Streams**: Characters flow along the floor, ceiling, and walls from near to far
- **Data Planes**: 25 wireframe rectangles spaced evenly through the tunnel depth
- **Error Messages**: Randomly positioned text that glitches and changes periodically
- **Longitudinal Lines**: Grid lines running through the tunnel for structure
- **Central Display**: A prominent "SYSTEM ERROR" warning floating in the middle distance

## Customisation

Edit `main.py` to adjust:

```python
# Number of matrix streams
rain_system = MatrixRainSystem(num_streams=400, bounds=bounds)

# Number of data planes
plane_system = DataPlaneSystem(num_planes=25, bounds=bounds)

# Window size (if windowed mode)
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

# Fullscreen mode
WINDOWED = False  # Set to False for fullscreen
```

Edit `data_planes.py` to customize error messages:

```python
ERROR_MESSAGES = [
    "YOUR CUSTOM MESSAGE",
    "ANOTHER ERROR",
    # Add more messages...
]
```

## Performance Tips

- Reduce `num_streams` in MatrixRainSystem for better performance
- Reduce `num_planes` in DataPlaneSystem for fewer data planes
- Close other applications using your webcam
- Ensure good lighting for better face tracking

## Troubleshooting

**Face tracking not working:**
- Ensure your webcam is connected and working
- Check that `face_landmarker.task` is in the correct location
- Try adjusting lighting conditions

**Low frame rate:**
- Reduce the number of visual elements (streams, planes)
- Use a lower resolution window
- Close background applications

**Import errors:**
- Verify all packages are installed: `pip install pygame opencv-python mediapipe`
- Ensure you're using Python 3.7 or higher

## Credits

- Built with [Pygame](https://www.pygame.org/)
- Face tracking powered by [MediaPipe](https://mediapipe.dev/)
- Inspired by The Matrix and cyberpunk aesthetics
- Code is 100% by me, README made with the assistance of Claude

## License

MIT License - feel free to use and modify for your own projects!

## Contributing
This is a personal project and I'm not accepting pull requests or contributions at this time. However, you're welcome to fork the repository and modify the code for your own use! If you create something cool with it, I'd love to hear about it.

---
