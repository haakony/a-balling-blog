"""News article generation module."""

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

class NewsGenerator:
    """Generates satirical news articles about balls."""
    
    def __init__(self):
        self.llm_provider = get_llm_provider()
        self.ball_types = [
            "tennis ball", "basketball", "soccer ball", "baseball", "volleyball",
            "golf ball", "ping pong ball", "bowling ball", "beach ball", "croquet ball",
            "billiard ball", "rugby ball", "football", "cricket ball", "hockey puck"
        ]
        self.categories = [
            "sports", "politics", "technology", "entertainment", "science",
            "business", "health", "education", "environment", "lifestyle"
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
            article = response.strip()
            
            # Remove any JSON-like artifacts
            article = re.sub(r'\{.*?\}', '', article, flags=re.DOTALL)
            article = re.sub(r'```.*?```', '', article, flags=re.DOTALL)
            article = re.sub(r'\[SCENE\]', '', article)
            
            # Clean up extra whitespace
            article = re.sub(r'\s+', ' ', article)
            article = article.strip()
            
            # Get the first sentence for the title
            first_sentence = article.split('.')[0] if '.' in article else article
            
            # Create safe image prompts
            safe_prompt = self._clean_image_prompt(f"news article illustration of {first_sentence}")
            
            return {
                "title": self._clean_title(f"Breaking: {first_sentence}"),
                "article": article,
                "category": random.choice(self.categories),
                "image_prompt": safe_prompt,
                "scene_prompt": safe_prompt
            }
    
    def generate_article(self) -> Dict[str, Any]:
        """Generate a complete news article with title, content, and images."""
        # Select random ball type and category
        ball_type = random.choice(self.ball_types)
        category = random.choice(self.categories)
        
        # Generate the article
        article_prompt = f"""Create a humorous fake news article about a {ball_type} in the {category} category.
The article should be around 300-400 words and follow a typical news article structure.
Make it engaging and humorous, but keep it family-friendly and safe.
Include a [SCENE] marker where you want an image to be inserted.

You must return a JSON object with exactly these fields:
{{
    "title": "A creative, engaging title for the article",
    "article": "The full article content with [SCENE] marker",
    "category": "{category}",
    "image_prompt": "A family-friendly prompt for generating the main image",
    "scene_prompt": "A family-friendly prompt for generating the scene image"
}}

Requirements:
1. The title should be catchy and newsworthy
2. The article should have proper paragraphs and formatting
3. Use the [SCENE] marker only once in the middle of the article
4. Keep all content family-friendly and safe
5. Avoid any violent or dangerous scenarios
6. Follow a typical news article structure with an introduction, body, and conclusion
7. Make the content engaging and humorous"""
        
        try:
            # Generate article content using the LLM provider
            article_json = self.llm_provider.generate_content(article_prompt)
            article_data = self._parse_json_response(article_json)
            
            # Validate and ensure all required fields are present
            required_fields = {
                "title": self._clean_title(f"Breaking: {ball_type.capitalize()} Makes Headlines"),
                "article": f"A humorous news article about a {ball_type} in the {category} category.",
                "category": category,
                "image_prompt": self._clean_image_prompt(f"news article illustration of {ball_type}"),
                "scene_prompt": self._clean_image_prompt(f"news article illustration of {ball_type}")
            }
            
            # Update missing fields with defaults
            for field, default_value in required_fields.items():
                if field not in article_data or not article_data[field]:
                    logger.warning(f"Missing or empty field: {field}, using default")
                    article_data[field] = default_value
            
            # Clean image prompts and title
            article_data['image_prompt'] = self._clean_image_prompt(article_data['image_prompt'])
            article_data['scene_prompt'] = self._clean_image_prompt(article_data['scene_prompt'])
            article_data['title'] = self._clean_title(article_data['title'])
            
            # Format the article content
            article_data['article'] = article_data['article'].replace('\n\n', '\n').strip()
            
            # Add model tags
            article_data['tags'] = [
                'news', 'humor', 'ball', 'satire', 'funny', 'generated', 'fake-news', 'parody',
                article_data['category'],
                self.llm_provider.__class__.__name__.lower().replace('provider', ''),
                self.llm_provider.model
            ]
            
            # Create the news article
            filename = create_blog_post(article_data, "", "", "news")
            
            return {
                'filename': filename,
                'article_data': article_data,
                'image_path': "",
                'scene_image_path': ""
            }
            
        except Exception as e:
            logger.error(f"Error generating article: {e}")
            raise 