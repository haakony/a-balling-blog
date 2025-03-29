#!/usr/bin/env python3
import os
import subprocess
from datetime import datetime
import requests
import json
import time
import random
import re

def generate_story():
    """Generate a short story using Ollama API"""
    url = "http://192.168.1.9:11434/api/generate"
    
    # List of different ball types to randomly choose from
    ball_types = [
        "basketball", "soccer ball", "tennis ball", "baseball", "volleyball", 
        "bouncy ball", "ping pong ball", "golf ball", "rugby ball", "cricket ball", 
        "beach ball", "pool ball", "bowling ball", "medicine ball", "football",
        "softball", "lacrosse ball", "hockey puck", "kickball", "dodgeball"
    ]
    
    # Randomly select a ball type
    selected_ball = random.choice(ball_types)
    
    prompt = f"""You are a creative writing assistant that generates stories in JSON format.
    Your task is to write a short, funny story about a {selected_ball}.
    
    The story should be around 300-400 words and be suitable for a blog post. 
    Make it engaging and humorous.
    
    Important guidelines:
    1. Start with a specific action involving the {selected_ball} (e.g., "The {selected_ball} was bouncing", "A {selected_ball} rolled")
    2. Create a unique scenario or problem
    3. Include specific locations or settings
    4. Avoid generic phrases like "The Great Ball Rebellion"
    5. Make the story specific and memorable
    6. Include a [SCENE] marker in the story where an illustration would be most impactful
    
    Example good starts:
    - "The {selected_ball} was bouncing through the empty gymnasium"
    - "A {selected_ball} rolled down the driveway"
    - "The {selected_ball} was flying through the park"
    
    After the story, add a "Summary:" section with exactly 3 lines that capture the key points of the story.
    
    You MUST return ONLY a valid JSON object with the following structure:
    {{
        "title": "A creative, engaging title for the story",
        "story": "The full story text with [SCENE] marker where appropriate",
        "summary": "The 3-line summary",
        "image_prompt": "A detailed prompt for generating an illustration of the story's key scene",
        "scene_prompt": "A detailed prompt for generating an illustration of the scene marked with [SCENE]"
    }}
    
    Do not include any other text, markdown formatting, or code blocks. Return ONLY the JSON object.
    Make sure the title is unique and reflects the specific action and situation in the story."""
    
    data = {
        #"model": "gemma3:12b",
        "model": "llama3.1:8b",
        "keep_alive": 0,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        result = response.json()["response"]
        
        # Try to parse the JSON response
        try:
            # First try to parse the entire response
            story_data = json.loads(result)
        except json.JSONDecodeError:
            print("Failed to parse full JSON response, trying to extract JSON from text...")
            # Try to find JSON-like content between triple backticks if present
            json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', result, re.DOTALL)
            if json_match:
                try:
                    story_data = json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    print("Failed to parse JSON from code block, falling back to text format")
                    story_data = None
            else:
                print("No JSON found in response, falling back to text format")
                story_data = None
        
        # If we still don't have valid JSON, fall back to text format
        if not story_data:
            print("Falling back to text format...")
            parts = result.split("Summary:")
            story = parts[0].strip()
            summary = parts[1].strip() if len(parts) > 1 else ""
            story_data = {
                "title": f"The {selected_ball.capitalize()}'s Adventure",
                "story": story,
                "summary": summary,
                "image_prompt": f"funny realistic illustration of {story.split('.')[0]}",
                "scene_prompt": f"funny realistic illustration of {story.split('.')[0]}"
            }
        
        # Validate the required fields
        required_fields = ["title", "story", "summary", "image_prompt", "scene_prompt"]
        for field in required_fields:
            if field not in story_data:
                print(f"Missing required field: {field}")
                story_data[field] = f"Missing {field}"
        
        # Clean up any markdown formatting that might have slipped through
        for field in story_data:
            if isinstance(story_data[field], str):
                story_data[field] = story_data[field].replace('```json', '').replace('```', '').strip()
        
        return story_data
        
    except Exception as e:
        print(f"Error generating story: {e}")
        return None

def generate_image(story_data):
    """Generate an image using ComfyUI API"""
    base_url = "http://192.168.1.9:7860"
    headers = {
        "Content-Type": "application/json"
    }
    
    # Use the image prompt from the story data
    image_prompt = f"""{story_data['image_prompt']}, 
    cute and humorous, vibrant colors, clean lines, 
    detailed background, high quality, realistic, detailed, 4k, 8k """
    
    # ComfyUI workflow for text-to-image
    workflow = {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": int(datetime.now().timestamp()),
                "steps": 30,  # SD3 models work well with fewer steps
                "cfg": 7,     # Lower CFG for SD3 models
                "sampler_name": "dpmpp_2m",  # DPM++ sampler works better with SD3
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
                "ckpt_name": "sd3_medium_incl_clips_t5xxlfp16.safetensors"
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
                "filename_prefix": "ComfyUI",
                "images": ["8", 0]
            }
        }
    }
    
    try:
        print("Generating image with ComfyUI...")
        response = requests.post(f"{base_url}/prompt", headers=headers, json={"prompt": workflow})
        
        if response.status_code != 200:
            print(f"Error generating image: {response.text}")
            return None, None
            
        prompt_id = response.json()['prompt_id']
        print(f"Image generation started with prompt ID: {prompt_id}")
        
        # Wait for the image to be generated
        while True:
            history = requests.get(f"{base_url}/history/{prompt_id}").json()
            if prompt_id in history:
                if 'outputs' in history[prompt_id]:
                    outputs = history[prompt_id]['outputs']
                    if '9' in outputs:  # Our SaveImage node
                        image_data = outputs['9']['images'][0]
                        
                        # Create Hugo static/images directory if it doesn't exist
                        images_dir = "static/images"
                        os.makedirs(images_dir, exist_ok=True)
                        
                        # Generate a unique filename based on the story content
                        timestamp = datetime.now().strftime("%H%M%S")
                        
                        # Extract key elements from the story for the filename
                        first_sentence = story_data['story'].split('.')[0].lower()
                        ball_types = ['basketball', 'football', 'soccer ball', 'tennis ball', 'baseball', 'volleyball', 'bouncy ball', 'ping pong ball', 'ball', 'golf ball', 'rugby ball', 'cricket ball', 'beach ball', 'pool ball', 'bowling ball', 'medicine ball']
                        action_words = ['bouncing', 'rolling', 'flying', 'jumping', 'dancing', 'playing', 'racing', 'dribbling', 'rebelling', 'misbehaving', 'escaping', 'adventuring', 'diving', 'splashing', 'floating', 'spinning', 'tumbling', 'leaping', 'skipping', 'bobbing']
                        
                        # Look for ball type and action in the first sentence
                        found_ball = next((ball for ball in ball_types if ball in first_sentence), None)
                        found_action = next((action for action in action_words if action in first_sentence), None)
                        
                        if found_ball and found_action:
                            filename = f"{found_action}-{found_ball}-{timestamp}.png"
                        elif found_ball:
                            filename = f"{found_ball}-{timestamp}.png"
                        elif found_action:
                            filename = f"{found_action}-ball-{timestamp}.png"
                        else:
                            # If no specific elements found, use a shortened version of the first sentence
                            words = first_sentence.split()[:3]
                            filename = f"{'-'.join(words)}-{timestamp}.png"
                        
                        # Clean up the filename
                        filename = ''.join(c for c in filename if c.isalnum() or c in '-_.')
                        hugo_filename = filename
                        hugo_path = os.path.join(images_dir, hugo_filename)
                        
                        # Download the image from ComfyUI
                        print(f"Downloading image from ComfyUI...")
                        image_url = f"{base_url}/view?filename={image_data['filename']}&subfolder={image_data['subfolder']}&type={image_data['type']}"
                        image_response = requests.get(image_url)
                        
                        if image_response.status_code == 200:
                            # Save to Hugo static/images directory
                            with open(hugo_path, "wb") as f:
                                f.write(image_response.content)
                            print(f"Image saved to: {hugo_path}")
                            # Return both the filename and the image prompt
                            return hugo_filename, story_data['image_prompt']
                        else:
                            print(f"Failed to download image: {image_response.status_code}")
                            return None, None
                            
            print("Waiting for image generation...")
            time.sleep(1)
            
    except Exception as e:
        print(f"Error generating image: {e}")
        return None, None

def generate_scene_image(story_data):
    """Generate an image for the scene marked in the story"""
    base_url = "http://192.168.1.9:7860"
    headers = {
        "Content-Type": "application/json"
    }
    
    # Use the scene prompt from the story data
    image_prompt = f"""{story_data['scene_prompt']}, 
    cute and humorous, vibrant colors, clean lines, 
    detailed background, high quality, realistic, detailed, 4k, 8k """
    
    # Use the same workflow as generate_image
    workflow = {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": int(datetime.now().timestamp()),
                "steps": 30,
                "cfg": 7,
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
                "ckpt_name": "sd3_medium_incl_clips_t5xxlfp16.safetensors"
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
                "filename_prefix": "ComfyUI",
                "images": ["8", 0]
            }
        }
    }
    
    try:
        print("Generating scene image with ComfyUI...")
        response = requests.post(f"{base_url}/prompt", headers=headers, json={"prompt": workflow})
        
        if response.status_code != 200:
            print(f"Error generating scene image: {response.text}")
            return None
            
        prompt_id = response.json()['prompt_id']
        print(f"Scene image generation started with prompt ID: {prompt_id}")
        
        # Wait for the image to be generated
        while True:
            history = requests.get(f"{base_url}/history/{prompt_id}").json()
            if prompt_id in history:
                if 'outputs' in history[prompt_id]:
                    outputs = history[prompt_id]['outputs']
                    if '9' in outputs:  # Our SaveImage node
                        image_data = outputs['9']['images'][0]
                        
                        # Create Hugo static/images directory if it doesn't exist
                        images_dir = "static/images"
                        os.makedirs(images_dir, exist_ok=True)
                        
                        # Generate a unique filename for the scene image
                        timestamp = datetime.now().strftime("%H%M%S")
                        scene_filename = f"scene-{timestamp}.png"
                        scene_path = os.path.join(images_dir, scene_filename)
                        
                        # Download the image from ComfyUI
                        print(f"Downloading scene image from ComfyUI...")
                        image_url = f"{base_url}/view?filename={image_data['filename']}&subfolder={image_data['subfolder']}&type={image_data['type']}"
                        image_response = requests.get(image_url)
                        
                        if image_response.status_code == 200:
                            # Save to Hugo static/images directory
                            with open(scene_path, "wb") as f:
                                f.write(image_response.content)
                            print(f"Scene image saved to: {scene_path}")
                            return scene_filename
                        else:
                            print(f"Failed to download scene image: {image_response.status_code}")
                            return None
                            
            print("Waiting for scene image generation...")
            time.sleep(1)
            
    except Exception as e:
        print(f"Error generating scene image: {e}")
        return None

def create_blog_post(story_data, image_path, scene_image_path):
    """Create a new Hugo blog post with the generated content and image"""
    # Create the content directory if it doesn't exist
    content_dir = "content/en/posts"
    os.makedirs(content_dir, exist_ok=True)
    
    # Generate filename with current date
    current_date = datetime.now()
    date = current_date.strftime("%Y-%m-%d")
    timestamp = current_date.strftime("%H%M%S")
    
    # Use the title from story_data
    title = story_data['title']
    
    # Clean up the title
    title = title.replace('"', '').replace("'", '').replace('?', '').replace('!', '')
    title = ''.join(c for c in title[:60] if c.isalnum() or c.isspace() or c in '-')
    title = title.strip()
    
    # Create URL-friendly slug with timestamp to ensure uniqueness
    slug = title.lower().replace(' ', '-')
    filename = f"{content_dir}/{date}-{slug}-{timestamp}.md"
    
    # Format the image paths correctly for Hugo
    if image_path:
        if image_path.startswith('images/'):
            image_path = image_path[7:]
        image_path = f"/images/{image_path}"
    
    if scene_image_path:
        if scene_image_path.startswith('images/'):
            scene_image_path = scene_image_path[7:]
        scene_image_path = f"/images/{scene_image_path}"
    
    # Create the front matter and content
    front_matter = f"""---
title: "{title}"
date: {date}
draft: false
---

"""
    
    # Add the main image using markdown syntax if we have one, wrapped in a link
    image_section = f"\n[![image]({image_path})]({date}-{slug}-{timestamp})\n" if image_path else ""
    
    # Get the first part of the story (up to the first period)
    first_part = story_data['story'].split('.')[0] + '.'
    
    # Create introduction section with the first part of the story
    intro_section = f"""

{first_part}

"""
    
    # Process the story to insert the scene image
    story_parts = story_data['story'].split('[SCENE]')
    story_with_image = story_parts[0]
    if len(story_parts) > 1 and scene_image_path:
        story_with_image += f"\n\n[![scene]({scene_image_path})]({date}-{slug}-{timestamp})\n\n" + story_parts[1]
    else:
        story_with_image = story_data['story']
    
    # Add the prompts section at the end
    prompts_section = f"""

---

### Generation Details

#### Story Generation Prompt
```text
Write a short, funny story about a {story_data['story'].split('.')[0].split()[0]}. 
The story should be around 300-400 words and be suitable for a blog post. 
Make it engaging and humorous.
```

#### Image Generation Prompt
```text
{story_data['image_prompt']}
```

#### Scene Image Generation Prompt
```text
{story_data['scene_prompt']}
```

#### Image Generation Settings
- Resolution: 768x768
- Steps: 30
- CFG: 7
- Sampler: DPM++ 2M
- Model: sd3_medium_incl_clips_t5xxlfp16.safetensors
"""
    
    # Write the content to the file
    with open(filename, "w", encoding="utf-8") as f:
        f.write(front_matter + image_section + intro_section + "\n<!--more-->\n\n" + story_with_image + prompts_section)
    
    return filename

def deploy():
    """Run the deploy script"""
    try:
        subprocess.run(["./deploy.sh"], check=True)
        print("Deployment successful!")
    except subprocess.CalledProcessError as e:
        print(f"Deployment failed: {e}")

def main():
    print("Generating story...")
    story_data = generate_story()
    
    if story_data:
        print("Generating main image...")
        image_path, _ = generate_image(story_data)
        
        if image_path:
            print("Generating scene image...")
            scene_image_path = generate_scene_image(story_data)
            
            print("Creating blog post...")
            filename = create_blog_post(story_data, image_path, scene_image_path)
            print(f"Blog post created at: {filename}")
            
            print("Deploying...")
            deploy()
        else:
            print("Failed to generate main image. Creating post without images...")
            filename = create_blog_post(story_data, "", "")
            print(f"Blog post created at: {filename}")
            
            print("Deploying...")
            deploy()
    else:
        print("Failed to generate story. Please check if Ollama is running.")

if __name__ == "__main__":
    main()
