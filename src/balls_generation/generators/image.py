"""Image generation module."""

import os
from datetime import datetime
import logging

from ..image_providers import get_image_provider
from ..config.settings import IMAGES_DIR

logger = logging.getLogger(__name__)

class ImageGenerator:
    """Handles image generation using configured provider."""
    
    def __init__(self, provider_type: str = "dalle"):
        """Initialize the image generator with specified provider."""
        self.provider = get_image_provider(provider_type)
    
    def generate_image(self, prompt, prefix="image"):
        """Generate an image using the configured provider."""
        try:
            # Generate image using the provider
            logger.info(f"Generating {prefix} with {self.provider.__class__.__name__}...")
            image_url = self.provider.generate_image(prompt)
            
            if image_url:
                # Generate a unique filename
                timestamp = datetime.now().strftime("%H%M%S")
                filename = f"{prefix}-{timestamp}.png"
                filepath = os.path.join(IMAGES_DIR, filename)
                
                # Download and save the image
                logger.info(f"Downloading {prefix}...")
                if self.provider.download_and_save_image(image_url, filepath):
                    logger.info(f"{prefix.capitalize()} saved to: {filepath}")
                    return filename, prompt
                else:
                    logger.error(f"Failed to save {prefix}")
                    return None, None
            else:
                logger.error(f"Failed to generate {prefix}")
                return None, None
                
        except Exception as e:
            logger.error(f"Error generating {prefix}: {e}")
            return None, None
