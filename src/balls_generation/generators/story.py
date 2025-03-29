"""Story generation module."""

import json
import random
import re
from typing import Dict, Any, List
import logging
from datetime import datetime

from ..llm_providers import get_llm_provider
from ..utils.content import create_blog_post
from ..utils.images import download_and_save_image

logger = logging.getLogger(__name__)

class StoryGenerator:
    """Generates humorous stories about balls."""
    
    def __init__(self):
        self.llm_provider = get_llm_provider()
        self.ball_types = [
            "tennis ball", "basketball", "soccer ball", "baseball", "volleyball",
            "golf ball", "ping pong ball", "bowling ball", "beach ball", "croquet ball",
            "billiard ball", "rugby ball", "football", "cricket ball", "hockey puck"
        ]
    
    def _clean_image_prompt(self, prompt: str) -> str:
        """Clean and filter image prompts to avoid content policy violations."""
        # Remove any potentially problematic words
        problematic_words = ['violence', 'danger', 'harm', 'injury', 'damage', 'destruction']
        for word in problematic_words:
            prompt = prompt.replace(word, '')
        
        # Ensure the prompt is family-friendly
        prompt = f"family-friendly, safe, {prompt}"
        
        # Limit the length to avoid complex prompts
        return ' '.join(prompt.split()[:20])
    
    def _clean_title(self, title: str) -> str:
        """Clean and format the title to be URL-friendly."""
        # Remove any JSON-like artifacts
        title = re.sub(r'\{.*?\}', '', title, flags=re.DOTALL)
        title = re.sub(r'```.*?```', '', title, flags=re.DOTALL)
        
        # Remove special characters and extra whitespace
        title = re.sub(r'[^\w\s-]', '', title)
        title = re.sub(r'\s+', ' ', title)
        title = title.strip()
        
        # Capitalize first letter of each word
        title = ' '.join(word.capitalize() for word in title.split())
        
        return title
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON response, handling various formats and fallbacks."""
        try:
            # First try to parse the entire response
            return json.loads(response)
        except json.JSONDecodeError:
            logger.warning("Failed to parse full JSON response, trying to extract JSON from text...")
            
            # Try to find JSON-like content between triple backticks if present
            json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    logger.warning("Failed to parse JSON from code block")
            
            # If we still don't have valid JSON, create a structured response
            logger.info("Falling back to text format...")
            
            # Clean up the response text
            story = response.strip()
            
            # Remove any JSON-like artifacts
            story = re.sub(r'\{.*?\}', '', story, flags=re.DOTALL)
            story = re.sub(r'```.*?```', '', story, flags=re.DOTALL)
            story = re.sub(r'\[SCENE\]', '', story)
            
            # Clean up extra whitespace
            story = re.sub(r'\s+', ' ', story)
            story = story.strip()
            
            # Get the first sentence for the title
            first_sentence = story.split('.')[0] if '.' in story else story
            
            # Create safe image prompts
            safe_prompt = self._clean_image_prompt(f"funny realistic illustration of {first_sentence}")
            
            return {
                "title": self._clean_title(f"The {first_sentence}"),
                "story": story,
                "image_prompt": safe_prompt,
                "scene_prompt": safe_prompt
            }
    
    def generate_story(self) -> Dict[str, Any]:
        """Generate a complete story with title, content, and images."""
        # Select a random ball type
        ball_type = random.choice(self.ball_types)
        
        # Generate the story
        story_prompt = f"""Write a short, funny story about a {ball_type}. 
The story should be around 300-400 words and be suitable for a blog post. 
Make it engaging and humorous, but keep it family-friendly and safe.
Include a [SCENE] marker where you want an image to be inserted.

Return the story in this exact JSON format:
{{
    "title": "A creative title for the story",
    "story": "The story content with [SCENE] marker",
    "image_prompt": "A family-friendly prompt for generating the main image",
    "scene_prompt": "A family-friendly prompt for generating the scene image"
}}

Important: 
1. Return ONLY the JSON object, no additional text or formatting
2. Keep all content family-friendly and safe
3. Avoid any violent or dangerous scenarios
4. Make sure the story has proper paragraphs and formatting
5. Use the [SCENE] marker only once in the middle of the story"""
        
        try:
            # Generate story content using the LLM provider
            story_json = self.llm_provider.generate_content(story_prompt)
            story_data = self._parse_json_response(story_json)
            
            # Validate and ensure all required fields are present
            required_fields = {
                "title": self._clean_title(f"The {ball_type.capitalize()}'s Adventure"),
                "story": story_json,
                "image_prompt": self._clean_image_prompt(f"funny realistic illustration of {ball_type}"),
                "scene_prompt": self._clean_image_prompt(f"funny realistic illustration of {ball_type}")
            }
            
            # Update missing fields with defaults
            for field, default_value in required_fields.items():
                if field not in story_data or not story_data[field]:
                    logger.warning(f"Missing or empty field: {field}, using default")
                    story_data[field] = default_value
            
            # Clean image prompts and title
            story_data['image_prompt'] = self._clean_image_prompt(story_data['image_prompt'])
            story_data['scene_prompt'] = self._clean_image_prompt(story_data['scene_prompt'])
            story_data['title'] = self._clean_title(story_data['title'])
            
            # Format the story content
            story_data['story'] = story_data['story'].replace('\n\n', '\n').strip()
            
            # Add model tags
            story_data['tags'] = [
                'story', 'humor', 'ball', 'fiction', 'funny', 'adventure', 'random', 'generated',
                self.llm_provider.__class__.__name__.lower().replace('provider', ''),
                self.llm_provider.model
            ]
            
            # Create the blog post
            filename = create_blog_post(story_data, "", "", "story")
            
            return {
                'filename': filename,
                'story_data': story_data,
                'image_path': "",
                'scene_image_path': ""
            }
            
        except Exception as e:
            logger.error(f"Error generating story: {e}")
            raise
