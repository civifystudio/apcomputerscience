# 3D Chase Game

A simple 3D game where an image chases the player in a 3D environment.

## Requirements
- Python 3.7+
- Panda3D
- NumPy

## Installation
1. Install the required packages:
```bash
pip install -r requirements.txt
```

2. Add your chaser image:
- Place an image file named `chaser.png` in the same directory as `main.py`
- The image should preferably have a transparent background

## How to Play
1. Run the game:
```bash
python main.py
```

2. Controls:
- Use arrow keys to move around
- Up/Down arrows: Move forward/backward
- Left/Right arrows: Turn left/right
- ESC: Exit the game

## Features
- 3D environment
- Image that follows the player
- Smooth movement controls
- Billboarded image (always faces the camera)
