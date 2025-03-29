"""Configuration settings for the balls generation system."""

import os
from datetime import datetime

# API URLs
OLLAMA_API_URL = "http://192.168.1.9:11434/api/generate"
COMFYUI_API_URL = "http://192.168.1.9:7860"

# Directory paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
CONTENT_DIR = os.path.join(BASE_DIR, "content/en/posts")
IMAGES_DIR = os.path.join(BASE_DIR, "static/images")

# Ball types for story generation
BALL_TYPES = [
    "basketball", "soccer ball", "tennis ball", "baseball", "volleyball", 
    "bouncy ball", "ping pong ball", "golf ball", "rugby ball", "cricket ball", 
    "beach ball", "pool ball", "bowling ball", "medicine ball", "football",
    "softball", "lacrosse ball", "hockey puck", "kickball", "dodgeball"
]

# Image generation settings
IMAGE_SETTINGS = {
    "resolution": "768x768",
    "steps": 30,
    "cfg": 7,
    "sampler": "DPM++ 2M",
    "model": "sd3_medium_incl_clips_t5xxlfp16.safetensors"
}

# Create necessary directories
os.makedirs(CONTENT_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

# Logging
LOG_FILE = os.path.join(BASE_DIR, "cron.log")
