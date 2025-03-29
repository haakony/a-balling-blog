#!/usr/bin/env python3
import os
import requests
import json
from datetime import datetime
import time

def generate_image_with_model(prompt, model_name, base_url="http://192.168.1.9:7860"):
    """Generate an image using ComfyUI API with a specific model"""
    headers = {
        "Content-Type": "application/json"
    }
    
    # Skip inpainting models
    if "inpainting" in model_name.lower():
        print(f"Skipping inpainting model: {model_name}")
        return None
    
    # Create a more detailed prompt that emphasizes visual elements
    image_prompt = f"""{prompt}, 
    Fantasy landscape, dynamic lights, glowing emerald, nebulas, sunset, , 8k photorealistic eternal ambiente, alien plants, surealism sphere, giant mushrooms"""
    
    # Adjust settings based on model type
    if "sd3" in model_name.lower():
        # SD3 models might need different settings
        steps = 30
        cfg = 7
        sampler = "dpmpp_2m"  # SD3 models often work better with DPM++ samplers
    else:
        # Default settings for other models
        steps = 40
        cfg = 8
        sampler = "euler"
    
    # ComfyUI workflow for text-to-image
    workflow = {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": int(datetime.now().timestamp()),
                "steps": steps,
                "cfg": cfg,
                "sampler_name": sampler,
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
                "ckpt_name": model_name
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
                "text": image_prompt,
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
                "filename_prefix": f"ComfyUI_{model_name}",
                "images": ["8", 0]
            }
        }
    }
    
    try:
        print(f"Generating image with model {model_name}...")
        print(f"Using settings: steps={steps}, cfg={cfg}, sampler={sampler}")
        
        response = requests.post(f"{base_url}/prompt", headers=headers, json={"prompt": workflow})
        
        if response.status_code != 200:
            print(f"Error generating image with {model_name}: {response.text}")
            return None
            
        prompt_id = response.json()['prompt_id']
        print(f"Image generation started with prompt ID: {prompt_id}")
        
        # Add timeout for image generation (reduced to 2 minutes)
        start_time = time.time()
        timeout = 120  # 2 minutes timeout
        
        # Wait for the image to be generated
        while True:
            if time.time() - start_time > timeout:
                print(f"Timeout waiting for image generation with {model_name}")
                return None
                
            try:
                history = requests.get(f"{base_url}/history/{prompt_id}").json()
                if prompt_id in history:
                    if 'outputs' in history[prompt_id]:
                        outputs = history[prompt_id]['outputs']
                        if '9' in outputs:  # Our SaveImage node
                            image_data = outputs['9']['images'][0]
                            
                            # Create test_images directory if it doesn't exist
                            images_dir = "test_images"
                            os.makedirs(images_dir, exist_ok=True)
                            
                            # Generate a unique filename
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"{model_name}_{timestamp}.png"
                            filepath = os.path.join(images_dir, filename)
                            
                            # Download the image from ComfyUI
                            print(f"Downloading image from ComfyUI...")
                            image_url = f"{base_url}/view?filename={image_data['filename']}&subfolder={image_data['subfolder']}&type={image_data['type']}"
                            image_response = requests.get(image_url)
                            
                            if image_response.status_code == 200:
                                # Save the image
                                with open(filepath, "wb") as f:
                                    f.write(image_response.content)
                                print(f"Image saved to: {filepath}")
                                return filepath
                            else:
                                print(f"Failed to download image: {image_response.status_code}")
                                return None
            except Exception as e:
                print(f"Error checking history: {e}")
                time.sleep(1)
                continue
                            
            print("Waiting for image generation...")
            time.sleep(1)
            
    except Exception as e:
        print(f"Error generating image with {model_name}: {e}")
        return None

def get_available_models(base_url="http://192.168.1.9:7860"):
    """Get a list of available models from ComfyUI"""
    try:
        response = requests.get(f"{base_url}/object_info")
        if response.status_code == 200:
            object_info = response.json()
            # Look for the CheckpointLoaderSimple node info
            if "CheckpointLoaderSimple" in object_info:
                checkpoint_info = object_info["CheckpointLoaderSimple"]
                if "input" in checkpoint_info and "required" in checkpoint_info["input"]:
                    ckpt_input = checkpoint_info["input"]["required"]
                    if "ckpt_name" in ckpt_input:
                        # Get the list of available models
                        models = ckpt_input["ckpt_name"][0]
                        print("\nAvailable models:")
                        for model in models:
                            print(f"- {model}")
                        return models
        print("Could not get model list from ComfyUI")
        return []
    except Exception as e:
        print(f"Error getting available models: {e}")
        return []

def main():
    # Get available models first
    available_models = get_available_models()
    
    if not available_models:
        print("No models available. Please check if ComfyUI is running and has models loaded.")
        return
    
    # Test prompt
    test_prompt = "a funny cartoon of a basketball playing basketball with itself in a gym"
    
    # Filter out inpainting models and sort models to test SD3 models first
    text_to_image_models = [model for model in available_models if "inpainting" not in model.lower()]
    text_to_image_models.sort(key=lambda x: "sd3" in x.lower(), reverse=True)  # SD3 models first
    
    print(f"\nTesting {len(text_to_image_models)} available text-to-image models...")
    
    # Test each model
    for i, model in enumerate(text_to_image_models, 1):
        print(f"\nTesting model {i}/{len(text_to_image_models)}: {model}")
        result = generate_image_with_model(test_prompt, model)
        if result:
            print(f"Successfully generated image with {model}")
        else:
            print(f"Failed to generate image with {model}")
        
        # Wait a bit between models to avoid overwhelming the server
        time.sleep(2)
    
    print("\nTesting complete! Check the test_images directory for results.")

if __name__ == "__main__":
    main() 