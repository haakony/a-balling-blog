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
    """Ollama API provider implementation."""
    
    def __init__(self):
        self.api_url = os.getenv('OLLAMA_API_URL', 'http://192.168.1.9:11434')
        self.model = os.getenv('OLLAMA_MODEL', 'llama3.1:8b')
        logger.info(f"Initialized OllamaProvider with model: {self.model} at {self.api_url}")
    
    def generate_content(self, prompt: str) -> str:
        """Generate content using Ollama API."""
        logger.info(f"Generating content with Ollama at {self.api_url}")
        try:
            # Add system prompt to ensure proper JSON formatting
            system_prompt = """You are a creative writer who specializes in generating humorous stories and satirical news articles.
You must ALWAYS respond with a valid JSON object containing the requested fields.
Do not include any additional text, explanations, or formatting outside the JSON object.
The JSON must be properly formatted and complete."""
            
            response = requests.post(
                f"{self.api_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": f"{system_prompt}\n\n{prompt}",
                    "stream": False,
                    "format": "json"  # Request JSON format
                }
            )
            response.raise_for_status()
            
            # Get the response text
            response_text = response.json()['response']
            
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
                raise ValueError("Invalid JSON response from Ollama")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error connecting to Ollama API: {e}")
            raise
    
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