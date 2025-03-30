"""Story generation module."""

import json
import random
import re
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from ..llm_providers import get_llm_provider, OllamaProvider, OpenAIProvider
from ..image_providers import get_image_provider, ComfyUIProvider, DalleProvider
from ..utils.content import create_blog_post
from ..utils.images import download_and_save_image

# Configure logging
logger = logging.getLogger(__name__)

class StoryGenerator:
    """Generator for stories."""
    
    def __init__(self):
        self.llm_provider = get_llm_provider()
        self.image_provider = get_image_provider()
        self.ball_types = [
            "football", "basketball", "baseball", "tennis ball", "golf ball",
            "volleyball", "bowling ball", "billiard ball", "ping pong ball",
            "soccer ball", "rugby ball", "cricket ball", "hockey puck",
            "beach ball", "medicine ball", "stress ball", "bouncy ball"
        ]
    
    def generate_story(self) -> Optional[str]:
        """Generate a story."""
        try:
            # Select a random ball type
            ball_type = random.choice(self.ball_types)
            
            # Generate the story content
            prompt = f"""Write a short, funny story about a {ball_type}. 
            The story should be around 300-400 words and be suitable for a blog post. 
            Make it engaging and humorous.
            Include a [SCENE] marker where you want the scene image to be inserted.
            
            Return a JSON object with these fields:
            {{
                "title": "A creative, engaging title",
                "story": "The story content with [SCENE] marker",
                "category": "A relevant category",
                "tags": ["tag1", "tag2", "tag3"],
                "image_prompt": "A family-friendly prompt for the main image",
                "scene_prompt": "A family-friendly prompt for the scene image"
            }}
            
            Important:
            1. The story must include a [SCENE] marker where you want the scene image to appear
            2. The story should be properly formatted with paragraphs
            3. Keep all content family-friendly and safe
            4. Make the content engaging and humorous"""
            
            # Get the response from the LLM provider
            response = self.llm_provider.generate_content(prompt)
            
            # Parse the JSON response
            try:
                data = json.loads(response)
            except json.JSONDecodeError:
                logger.error("Failed to parse JSON response")
                return None
            
            # Clean the title and content
            title = self._clean_title(data.get('title', ''))
            content = self._clean_content(data.get('story', ''))
            
            # Ensure content has a [SCENE] marker
            if '[SCENE]' not in content:
                # Split content into paragraphs and insert [SCENE] after the first paragraph
                paragraphs = content.split('\n\n')
                if len(paragraphs) > 1:
                    content = paragraphs[0] + '\n\n[SCENE]\n\n' + '\n\n'.join(paragraphs[1:])
                else:
                    content = content + '\n\n[SCENE]\n\n'
            
            # Generate images
            image_path = None
            scene_image_path = None
            
            if self.image_provider:
                # Generate main image
                image_prompt = data.get('image_prompt', f"family-friendly, safe, story illustration of a {ball_type}")
                image_path = self.image_provider.generate_image(image_prompt)
                
                # Generate scene image
                scene_prompt = data.get('scene_prompt', f"family-friendly, safe, story illustration of a {ball_type} in action")
                scene_image_path = self.image_provider.generate_image(scene_prompt)
            
            # Get base tags from data or use defaults
            base_tags = data.get('tags', ['story', 'humor', 'ball', 'fiction', 'funny', 'adventure', 'random', 'generated'])
            
            # Add model tags
            if isinstance(self.llm_provider, OllamaProvider):
                base_tags.extend(['ollama', self.llm_provider.model])
            elif isinstance(self.llm_provider, OpenAIProvider):
                base_tags.extend(['openai', 'gpt-4'])
            
            if isinstance(self.image_provider, ComfyUIProvider):
                base_tags.extend(['comfyui', self.image_provider.model])
            elif isinstance(self.image_provider, DalleProvider):
                base_tags.extend(['dalle', self.image_provider.model])
            
            # Create the blog post
            filename = create_blog_post(
                data={
                    'title': title,
                    'story': content,
                    'category': data.get('category', 'general'),
                    'tags': base_tags,
                    'image_prompt': image_prompt if 'image_prompt' in locals() else '',
                    'scene_prompt': scene_prompt if 'scene_prompt' in locals() else ''
                },
                image_path=image_path,
                scene_image_path=scene_image_path,
                content_type="story"
            )
            
            return filename
            
        except Exception as e:
            logger.error(f"Error generating story: {str(e)}")
            return None
    
    def _clean_title(self, title: str) -> str:
        """Clean the title for use in filenames."""
        # Remove any JSON-like artifacts
        if title.startswith('{'):
            try:
                title_data = json.loads(title)
                title = title_data.get('title', title)
            except:
                pass
        
        # Remove any code blocks
        title = re.sub(r'```.*?```', '', title, flags=re.DOTALL)
        
        # Remove any JSON artifacts
        title = re.sub(r'\{.*?\}', '', title)
        
        # Remove any special characters and extra whitespace
        title = re.sub(r'[^\w\s-]', '', title)
        title = re.sub(r'\s+', ' ', title).strip()
        
        # Capitalize first letter of each word
        title = ' '.join(word.capitalize() for word in title.split())
        
        # Limit length
        if len(title) > 20:
            title = title[:20] + '...'
        
        return title
    
    def _clean_content(self, content: str) -> str:
        """Clean the content for use in the blog post."""
        # Remove any code blocks
        content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
        
        # Remove any JSON artifacts
        content = re.sub(r'\{.*?\}', '', content)
        
        # Remove any special characters and extra whitespace
        content = re.sub(r'[^\w\s.,!?-]', '', content)
        content = re.sub(r'\s+', ' ', content).strip()
        
        return content
