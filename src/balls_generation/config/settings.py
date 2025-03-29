"""Configuration settings for the balls generation system."""

import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API URLs and Keys
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://192.168.1.9:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
USE_OPENAI = os.getenv("USE_OPENAI", "false").lower() == "true"

# OpenAI Image Generation Settings
OPENAI_IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "dall-e-3")
OPENAI_IMAGE_QUALITY = os.getenv("OPENAI_IMAGE_QUALITY", "standard")
OPENAI_IMAGE_SIZE = os.getenv("OPENAI_IMAGE_SIZE", "1024x1024")

# ComfyUI Settings
COMFYUI_API_URL = os.getenv("COMFYUI_API_URL", "http://192.168.1.9:7860")
IMAGE_RESOLUTION = os.getenv("IMAGE_RESOLUTION", "768x768")
IMAGE_STEPS = int(os.getenv("IMAGE_STEPS", "30"))
IMAGE_CFG = float(os.getenv("IMAGE_CFG", "7"))
IMAGE_SAMPLER = os.getenv("IMAGE_SAMPLER", "DPM++ 2M")
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "sd3_medium_incl_clips_t5xxlfp16.safetensors")

# Image Provider Selection
IMAGE_PROVIDER = os.getenv("IMAGE_PROVIDER", "dalle")  # "dalle" or "comfyui"

# Content Generation Settings
MAX_STORY_LENGTH = int(os.getenv("MAX_STORY_LENGTH", "400"))
MAX_ARTICLE_LENGTH = int(os.getenv("MAX_ARTICLE_LENGTH", "400"))

# Site Configuration
SITE_URL = os.getenv("SITE_URL", "https://balls.no")
SITE_TITLE = os.getenv("SITE_TITLE", "A Balling Site")
SITE_DESCRIPTION = os.getenv("SITE_DESCRIPTION", "AI-generated stories and news about balls")

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

# Create necessary directories
os.makedirs(CONTENT_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

# Logging
LOG_FILE = os.path.join(BASE_DIR, "cron.log")
