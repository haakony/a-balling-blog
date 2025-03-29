"""Story generation module using Ollama API."""

import json
import random
import re
import requests
from datetime import datetime

from ..config.settings import OLLAMA_API_URL, BALL_TYPES

class StoryGenerator:
    """Handles story generation using the Ollama API."""
    
    def __init__(self):
        """Initialize the story generator."""
        self.url = OLLAMA_API_URL
    
    def generate_story(self):
        """Generate a short story using Ollama API."""
        # Randomly select a ball type
        selected_ball = random.choice(BALL_TYPES)
        
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
            "model": "gemma3:12b",
            "keep_alive": 0,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        
        try:
            response = requests.post(self.url, json=data)
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
