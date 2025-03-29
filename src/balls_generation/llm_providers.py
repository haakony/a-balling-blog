"""LLM provider implementations for content generation."""

import os
from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

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

class OllamaProvider(LLMProvider):
    """Ollama API provider implementation."""
    
    def __init__(self):
        self.api_url = os.getenv('OLLAMA_API_URL', 'http://localhost:11434')
        self.model = os.getenv('OLLAMA_MODEL', 'llama2')
        logger.info(f"Initialized OllamaProvider with model: {self.model}")
    
    def generate_content(self, prompt: str) -> str:
        """Generate content using Ollama API."""
        logger.info("Generating content with Ollama")
        response = requests.post(
            f"{self.api_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
        )
        response.raise_for_status()
        return response.json()['response']

class OpenAIProvider(LLMProvider):
    """OpenAI API provider implementation."""
    
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        logger.info(f"Initialized OpenAIProvider with model: {self.model}")
    
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