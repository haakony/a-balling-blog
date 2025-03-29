"""Image generation providers module."""

import os
import logging
from abc import ABC, abstractmethod
from datetime import datetime
import requests

from .config.settings import (
    IMAGES_DIR, OPENAI_API_KEY, OPENAI_IMAGE_MODEL,
    OPENAI_IMAGE_QUALITY, OPENAI_IMAGE_SIZE,
    COMFYUI_API_URL, IMAGE_STEPS, IMAGE_CFG, IMAGE_SAMPLER, IMAGE_MODEL
)

logger = logging.getLogger(__name__)

class ImageProvider(ABC):
    """Base class for image generation providers."""
    
    @abstractmethod
    def generate_image(self, prompt: str) -> str:
        """Generate an image from a prompt and return the URL."""
        pass
    
    def download_and_save_image(self, image_url: str, filepath: str) -> bool:
        """Download and save an image from a URL."""
        try:
            response = requests.get(image_url)
            if response.status_code == 200:
                with open(filepath, "wb") as f:
                    f.write(response.content)
                return True
            else:
                logger.error(f"Failed to download image: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error downloading image: {e}")
            return False

class DalleProvider(ImageProvider):
    """DALL-E image generation provider."""
    
    def __init__(self, api_key: str = None):
        """Initialize the DALL-E provider."""
        self.api_key = api_key or OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables")
            
        self.api_url = "https://api.openai.com/v1/images/generations"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_image(self, prompt: str) -> str:
        """Generate an image using DALL-E API."""
        try:
            data = {
                "model": OPENAI_IMAGE_MODEL,
                "prompt": prompt,
                "n": 1,
                "size": OPENAI_IMAGE_SIZE,
                "quality": OPENAI_IMAGE_QUALITY
            }
            
            response = requests.post(self.api_url, headers=self.headers, json=data)
            if response.status_code == 200:
                return response.json()["data"][0]["url"]
            else:
                logger.error(f"DALL-E API error: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error generating image with DALL-E: {e}")
            return None

class ComfyUIProvider(ImageProvider):
    """ComfyUI image generation provider."""
    
    def __init__(self, base_url: str = None):
        """Initialize the ComfyUI provider."""
        self.base_url = base_url or COMFYUI_API_URL
        self.headers = {"Content-Type": "application/json"}
    
    def _create_workflow(self, prompt: str) -> dict:
        """Create the ComfyUI workflow configuration."""
        return {
            "3": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": int(datetime.now().timestamp()),
                    "steps": IMAGE_STEPS,
                    "cfg": IMAGE_CFG,
                    "sampler_name": IMAGE_SAMPLER,
                    "scheduler": "normal",
                    "denoise": 1,
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0]
                }
            },
            "4": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {
                    "ckpt_name": IMAGE_MODEL
                }
            },
            "5": {
                "class_type": "EmptyLatentImage",
                "inputs": {
                    "batch_size": 1,
                    "height": 768,
                    "width": 768
                }
            },
            "6": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": prompt,
                    "clip": ["4", 1]
                }
            },
            "7": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": "blurry, bad quality, distorted, deformed, ugly, amateur, low resolution, pixelated, grainy, text, watermark, signature",
                    "clip": ["4", 1]
                }
            },
            "8": {
                "class_type": "VAEDecode",
                "inputs": {
                    "samples": ["3", 0],
                    "vae": ["4", 2]
                }
            },
            "9": {
                "class_type": "SaveImage",
                "inputs": {
                    "filename_prefix": "ComfyUI",
                    "images": ["8", 0]
                }
            }
        }
    
    def generate_image(self, prompt: str) -> str:
        """Generate an image using ComfyUI API."""
        try:
            workflow = self._create_workflow(prompt)
            response = requests.post(f"{self.base_url}/prompt", headers=self.headers, json={"prompt": workflow})
            
            if response.status_code != 200:
                logger.error(f"ComfyUI API error: {response.text}")
                return None
            
            prompt_id = response.json()['prompt_id']
            
            # Wait for the image to be generated
            while True:
                history = requests.get(f"{self.base_url}/history/{prompt_id}").json()
                if prompt_id in history and 'outputs' in history[prompt_id]:
                    outputs = history[prompt_id]['outputs']
                    if '9' in outputs:
                        image_data = outputs['9']['images'][0]
                        return f"{self.base_url}/view?filename={image_data['filename']}&subfolder={image_data['subfolder']}&type={image_data['type']}"
                
                import time
                time.sleep(1)
                
        except Exception as e:
            logger.error(f"Error generating image with ComfyUI: {e}")
            return None

def get_image_provider(provider_type: str = None) -> ImageProvider:
    """Get the appropriate image provider based on configuration."""
    provider_type = provider_type or IMAGE_PROVIDER
    
    if provider_type == "dalle":
        return DalleProvider()
    elif provider_type == "comfyui":
        return ComfyUIProvider()
    else:
        raise ValueError(f"Unknown image provider type: {provider_type}") 