"""News article generation module using Ollama API."""

import json
import random
import re
import requests
from datetime import datetime

from ..config.settings import OLLAMA_API_URL, BALL_TYPES

class NewsGenerator:
    """Handles news article generation using the Ollama API."""
    
    def __init__(self):
        """Initialize the news generator."""
        self.url = OLLAMA_API_URL
    
    def generate_article(self):
        """Generate a fake news article using Ollama API."""
        # Randomly select a ball type
        selected_ball = random.choice(BALL_TYPES)
        
        # Randomly select a news category
        news_categories = [
            "breaking news", "exclusive", "investigation", "sports", "technology",
            "entertainment", "science", "local news", "international", "business"
        ]
        category = random.choice(news_categories)
        
        prompt = f"""You are a creative writing assistant that generates fake news articles in JSON format.
        Your task is to write a humorous fake news article about a {selected_ball} in the {category} category.
        
        The article should be around 300-400 words and follow a typical news article structure:
        1. Start with a catchy headline
        2. Include a lead paragraph that summarizes the key points
        3. Add quotes from "experts" or "witnesses"
        4. Include some absurd but entertaining details
        5. End with a humorous twist or unexpected conclusion
        
        Important guidelines:
        1. Make it sound like a real news article but with absurd content
        2. Include specific locations, dates, and "facts"
        3. Use journalistic language and structure
        4. Include a [SCENE] marker where an illustration would be most impactful
        5. Make it entertaining but not offensive
        
        You MUST return ONLY a valid JSON object with the following structure:
        {{
            "title": "A catchy, news-style headline",
            "category": "The news category",
            "date": "A realistic date for the article",
            "article": "The full article text with [SCENE] marker where appropriate",
            "image_prompt": "A detailed prompt for generating an illustration of the article's key scene",
            "scene_prompt": "A detailed prompt for generating an illustration of the scene marked with [SCENE]",
            "tags": ["news", "humor", "ball", "satire", "funny", "generated", "fake-news", "parody", "{category}"]
        }}
        
        Do not include any other text, markdown formatting, or code blocks. Return ONLY the JSON object."""
        
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
                article_data = json.loads(result)
            except json.JSONDecodeError:
                print("Failed to parse full JSON response, trying to extract JSON from text...")
                # Try to find JSON-like content between triple backticks if present
                json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', result, re.DOTALL)
                if json_match:
                    try:
                        article_data = json.loads(json_match.group(1))
                    except json.JSONDecodeError:
                        print("Failed to parse JSON from code block, falling back to text format")
                        article_data = None
                else:
                    print("No JSON found in response, falling back to text format")
                    article_data = None
            
            # If we still don't have valid JSON, fall back to text format
            if not article_data:
                print("Falling back to text format...")
                article_data = {
                    "title": f"Breaking: {selected_ball.capitalize()} Makes Headlines",
                    "category": category,
                    "date": datetime.now().strftime("%B %d, %Y"),
                    "article": result,
                    "image_prompt": f"news article illustration of {selected_ball}",
                    "scene_prompt": f"news article illustration of {selected_ball}",
                    "tags": ["news", "humor", "ball", "satire", "funny", "generated", "fake-news", "parody", category]
                }
            
            # Validate the required fields
            required_fields = ["title", "category", "date", "article", "image_prompt", "scene_prompt", "tags"]
            for field in required_fields:
                if field not in article_data:
                    print(f"Missing required field: {field}")
                    if field == "tags":
                        article_data[field] = ["news", "humor", "ball", "satire", "funny", "generated", "fake-news", "parody", category]
                    else:
                        article_data[field] = f"Missing {field}"
            
            # Clean up any markdown formatting that might have slipped through
            for field in article_data:
                if isinstance(article_data[field], str):
                    article_data[field] = article_data[field].replace('```json', '').replace('```', '').strip()
            
            return article_data
            
        except Exception as e:
            print(f"Error generating news article: {e}")
            return None 