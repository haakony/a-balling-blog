"""LLM provider implementations for content generation."""

import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
import re
import json

from openai import OpenAI
from dotenv import load_dotenv
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def generate_content(self, prompt: str) -> str:
        """Generate content from a prompt."""
        pass
    
    @abstractmethod
    def generate_image(self, prompt: str) -> Optional[str]:
        """Generate an image from a prompt.
        
        Returns:
            Optional[str]: URL of the generated image, or None if image generation is not supported
        """
        pass

class OllamaProvider(LLMProvider):
    """Provider for Ollama API."""
    
    def __init__(self, model: str = None):
        self.model = model or os.getenv('OLLAMA_MODEL', 'llama2')
        self.api_url = os.getenv('OLLAMA_API_URL', 'http://192.168.1.9:11434')
        self.api_key = os.getenv('OLLAMA_API_KEY')
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        logger.info(f"Initialized OllamaProvider with model: {self.model} at {self.api_url}")
    
    def generate_content(self, prompt: str) -> str:
        """Generate text using Ollama API."""
        try:
            # Add system prompt to ensure JSON output
            system_prompt = """You are a helpful assistant that generates content in JSON format.
            You must ALWAYS respond with a valid JSON object containing these exact fields:
            {
                "title": "A creative, engaging title",
                "story": "The story content with proper paragraphs",
                "category": "A relevant category",
                "tags": ["tag1", "tag2", "tag3"],
                "image_prompt": "A family-friendly prompt for the main image",
                "scene_prompt": "A family-friendly prompt for the scene image"
            }
            
            Important rules:
            1. Return ONLY the JSON object, no additional text
            2. Use double quotes for all strings
            3. Include all required fields
            4. Keep content family-friendly and safe
            5. Make the story engaging and humorous
            6. Use proper paragraph breaks in the story content"""
            
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\nAssistant:"
            
            response = requests.post(
                f"{self.api_url}/api/generate",
                headers=self.headers,
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "keep_alive": 0,  # Prevent keeping VRAM full
                    "format": "json"  # Request JSON format
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')
                
                # Try to extract JSON if the response includes markdown code blocks
                if '```json' in response_text:
                    json_match = re.search(r'```json\s*({.*?})\s*```', response_text, re.DOTALL)
                    if json_match:
                        response_text = json_match.group(1)
                
                # Validate that we have a JSON object
                try:
                    json.loads(response_text)
                    return response_text
                except json.JSONDecodeError:
                    logger.error("Ollama response is not valid JSON")
                    # Create a fallback JSON response
                    return json.dumps({
                        "title": "The Ball's Adventure",
                        "story": "A humorous story about a ball.",
                        "category": "general",
                        "tags": ["story", "humor", "ball"],
                        "image_prompt": "family-friendly illustration of a ball",
                        "scene_prompt": "family-friendly scene with a ball"
                    })
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return ""
                
        except Exception as e:
            logger.error(f"Error generating content with Ollama: {str(e)}")
            return ""
    
    def generate_image(self, prompt: str) -> Optional[str]:
        """Ollama doesn't support image generation."""
        logger.warning("Image generation not supported by Ollama")
        return None

class OpenAIProvider(LLMProvider):
    """OpenAI API provider implementation."""
    
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        self.image_model = os.getenv('OPENAI_IMAGE_MODEL', 'dall-e-3')
        self.image_quality = os.getenv('OPENAI_IMAGE_QUALITY', 'standard')
        self.image_size = os.getenv('OPENAI_IMAGE_SIZE', '1024x1024')
        logger.info(f"Initialized OpenAIProvider with model: {self.model} and image model: {self.image_model}")
    
    def generate_content(self, prompt: str) -> str:
        """Generate content using OpenAI API."""
        logger.info("Generating content with OpenAI")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a creative writer who specializes in humorous stories and satirical news articles about balls."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=int(os.getenv('MAX_STORY_LENGTH', 400))
        )
        return response.choices[0].message.content
    
    def generate_image(self, prompt: str) -> Optional[str]:
        """Generate an image using DALL-E."""
        logger.info(f"Generating image with {self.image_model}")
        try:
            response = self.client.images.generate(
                model=self.image_model,
                prompt=prompt,
                size=self.image_size,
                quality=self.image_quality,
                n=1
            )
            return response.data[0].url
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return None

def get_llm_provider() -> LLMProvider:
    """Factory function to get the configured LLM provider."""
    use_openai_str = os.getenv('USE_OPENAI', 'false')
    # Strip quotes and whitespace, then convert to lowercase
    use_openai = use_openai_str.strip('"\'').strip().lower() == 'true'
    
    logger.info(f"USE_OPENAI environment variable: {use_openai_str}")
    logger.info(f"use_openai parsed value: {use_openai}")
    
    if use_openai:
        logger.info("Creating OpenAI provider")
        return OpenAIProvider()
    logger.info("Creating Ollama provider")
    return OllamaProvider() 