"""Image generation provider implementations."""

import os
import logging
import time
from abc import ABC, abstractmethod
from typing import Optional
import requests
from datetime import datetime
from dotenv import load_dotenv

from openai import OpenAI

# Get logger without configuring it
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class ImageProvider(ABC):
    """Abstract base class for image providers."""
    
    @abstractmethod
    def generate_image(self, prompt: str) -> Optional[str]:
        """Generate an image from a prompt.
        
        Returns:
            Optional[str]: Path to the generated image, or None if generation failed
        """
        pass

class DalleProvider(ImageProvider):
    """DALL-E image generation provider."""
    
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv('OPENAI_IMAGE_MODEL', 'dall-e-3')
        self.quality = os.getenv('OPENAI_IMAGE_QUALITY', 'standard')
        self.size = os.getenv('OPENAI_IMAGE_SIZE', '1024x1024')
        logger.info(f"Initialized DalleProvider with model: {self.model}")
    
    def generate_image(self, prompt: str) -> Optional[str]:
        """Generate an image using DALL-E."""
        logger.info(f"Generating image with {self.model}")
        try:
            response = self.client.images.generate(
                model=self.model,
                prompt=prompt,
                size=self.size,
                quality=self.quality,
                n=1
            )
            
            # Create images directory if it doesn't exist
            images_dir = "static/images"
            os.makedirs(images_dir, exist_ok=True)
            
            # Generate a unique filename
            timestamp = datetime.now().strftime("%H%M%S")
            filename = f"dalle-{timestamp}.png"
            filepath = os.path.join(images_dir, filename)
            
            # Download and save the image
            image_url = response.data[0].url
            image_response = requests.get(image_url)
            
            if image_response.status_code == 200:
                with open(filepath, "wb") as f:
                    f.write(image_response.content)
                logger.info(f"Image saved to: {filepath}")
                return filename
            else:
                logger.error(f"Failed to download image: {image_response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return None

class ComfyUIProvider(ImageProvider):
    """ComfyUI image generation provider."""
    
    def __init__(self):
        self.api_url = os.getenv('COMFYUI_API_URL', 'http://192.168.1.9:7860')
        self.resolution = os.getenv('IMAGE_RESOLUTION', '768x768')
        self.steps = int(os.getenv('IMAGE_STEPS', '30'))
        self.cfg = float(os.getenv('IMAGE_CFG', '7'))
        self.sampler = os.getenv('IMAGE_SAMPLER', 'DPM++ 2M')
        self.model = os.getenv('IMAGE_MODEL', 'sd3_medium_incl_clips_t5xxlfp16.safetensors')
        logger.info(f"Initialized ComfyUIProvider with model: {self.model}")
    
    def generate_image(self, prompt: str) -> Optional[str]:
        """Generate an image using ComfyUI."""
        logger.info(f"Generating image with ComfyUI at {self.api_url}")
        
        # ComfyUI workflow for text-to-image
        workflow = {
            "3": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": int(datetime.now().timestamp()),
                    "steps": self.steps,
                    "cfg": self.cfg,
                    "sampler_name": "dpmpp_2m",
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
                    "ckpt_name": self.model
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
                    "text": f"{prompt}, cute and humorous, vibrant colors, clean lines, detailed background, high quality, realistic, detailed, 4k, 8k",
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
        
        try:
            # Start the image generation
            response = requests.post(f"{self.api_url}/prompt", json={"prompt": workflow})
            if response.status_code != 200:
                logger.error(f"Error starting image generation: {response.text}")
                return None
            
            prompt_id = response.json()['prompt_id']
            logger.info(f"Image generation started with prompt ID: {prompt_id}")
            
            # Wait for the image to be generated
            while True:
                history = requests.get(f"{self.api_url}/history/{prompt_id}").json()
                if prompt_id in history:
                    if 'outputs' in history[prompt_id]:
                        outputs = history[prompt_id]['outputs']
                        if '9' in outputs:  # Our SaveImage node
                            image_data = outputs['9']['images'][0]
                            
                            # Create images directory if it doesn't exist
                            images_dir = "static/images"
                            os.makedirs(images_dir, exist_ok=True)
                            
                            # Generate a unique filename
                            timestamp = datetime.now().strftime("%H%M%S")
                            filename = f"comfyui-{timestamp}.png"
                            filepath = os.path.join(images_dir, filename)
                            
                            # Download the image
                            image_url = f"{self.api_url}/view?filename={image_data['filename']}&subfolder={image_data['subfolder']}&type={image_data['type']}"
                            image_response = requests.get(image_url)
                            
                            if image_response.status_code == 200:
                                with open(filepath, "wb") as f:
                                    f.write(image_response.content)
                                logger.info(f"Image saved to: {filepath}")
                                return filename
                            else:
                                logger.error(f"Failed to download image: {image_response.status_code}")
                                return None
                
                logger.info("Waiting for image generation...")
                time.sleep(1)
                
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return None

def get_image_provider() -> ImageProvider:
    """Factory function to get the configured image provider."""
    provider = os.getenv('IMAGE_PROVIDER', 'dalle').lower()
    
    if provider == 'dalle':
        logger.info("Creating DALL-E provider")
        return DalleProvider()
    elif provider == 'comfyui':
        logger.info("Creating ComfyUI provider")
        return ComfyUIProvider()
    else:
        raise ValueError(f"Unknown image provider: {provider}") 