"""Main script for generating content."""

import os
import random
import logging
from datetime import datetime

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from .generators.story import StoryGenerator
from .generators.news import NewsGenerator
from .image_providers import get_image_provider

logger = logging.getLogger(__name__)

def main():
    """Main function to generate content."""
    try:
        # Initialize generators
        story_generator = StoryGenerator()
        news_generator = NewsGenerator()
        
        # Randomly choose between story and news
        if random.random() < 0.5:
            logger.info("Generating story...")
            filename = story_generator.generate_story()
            if not filename:
                logger.error("Failed to generate story")
                return
        else:
            logger.info("Generating news article...")
            filename = news_generator.generate_article()
            if not filename:
                logger.error("Failed to generate article")
                return
        
        logger.info(f"Successfully generated content: {filename}")
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main() 