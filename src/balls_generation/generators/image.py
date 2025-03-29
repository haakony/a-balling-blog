"""Image generation module using ComfyUI API."""

import os
import time
import requests
from datetime import datetime

from ..config.settings import COMFYUI_API_URL, IMAGES_DIR, IMAGE_SETTINGS

class ImageGenerator:
    """Handles image generation using the ComfyUI API."""
    
    def __init__(self):
        """Initialize the image generator."""
        self.base_url = COMFYUI_API_URL
        self.headers = {"Content-Type": "application/json"}
    
    def _create_workflow(self, prompt):
        """Create the ComfyUI workflow configuration."""
        return {
            "3": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": int(datetime.now().timestamp()),
                    "steps": IMAGE_SETTINGS["steps"],
                    "cfg": IMAGE_SETTINGS["cfg"],
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
                    "ckpt_name": IMAGE_SETTINGS["model"]
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
    
    def generate_image(self, prompt, prefix="image"):
        """Generate an image using ComfyUI API."""
        try:
            # Create the workflow
            workflow = self._create_workflow(prompt)
            
            # Start the image generation
            print(f"Generating {prefix} with ComfyUI...")
            response = requests.post(f"{self.base_url}/prompt", headers=self.headers, json={"prompt": workflow})
            
            if response.status_code != 200:
                print(f"Error generating {prefix}: {response.text}")
                return None, None
                
            prompt_id = response.json()['prompt_id']
            print(f"{prefix.capitalize()} generation started with prompt ID: {prompt_id}")
            
            # Wait for the image to be generated
            while True:
                history = requests.get(f"{self.base_url}/history/{prompt_id}").json()
                if prompt_id in history:
                    if 'outputs' in history[prompt_id]:
                        outputs = history[prompt_id]['outputs']
                        if '9' in outputs:  # Our SaveImage node
                            image_data = outputs['9']['images'][0]
                            
                            # Generate a unique filename
                            timestamp = datetime.now().strftime("%H%M%S")
                            filename = f"{prefix}-{timestamp}.png"
                            filepath = os.path.join(IMAGES_DIR, filename)
                            
                            # Download the image from ComfyUI
                            print(f"Downloading {prefix} from ComfyUI...")
                            image_url = f"{self.base_url}/view?filename={image_data['filename']}&subfolder={image_data['subfolder']}&type={image_data['type']}"
                            image_response = requests.get(image_url)
                            
                            if image_response.status_code == 200:
                                # Save the image
                                with open(filepath, "wb") as f:
                                    f.write(image_response.content)
                                print(f"{prefix.capitalize()} saved to: {filepath}")
                                return filename, prompt
                            else:
                                print(f"Failed to download {prefix}: {image_response.status_code}")
                                return None, None
                                
                print(f"Waiting for {prefix} generation...")
                time.sleep(1)
                
        except Exception as e:
            print(f"Error generating {prefix}: {e}")
            return None, None
