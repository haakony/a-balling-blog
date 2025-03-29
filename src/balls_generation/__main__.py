"""Main entry point for the balls generation system."""

import os
import random
from datetime import datetime

from .generators.story import StoryGenerator
from .generators.news import NewsGenerator
from .generators.image import ImageGenerator
from .utils.deploy import deploy

def main():
    """Main entry point for the balls generation system."""
    print("Starting balls generation process...")
    
    # Initialize generators
    story_generator = StoryGenerator()
    news_generator = NewsGenerator()
    
    # Randomly choose between story and news article
    content_type = random.choice(["story", "news"])
    
    if content_type == "story":
        # Generate story
        print("Generating story...")
        story_data = story_generator.generate_story()
        
        if story_data:
            # Create blog post without images for now
            print("Creating blog post...")
            filename = story_data['filename']
            print(f"Blog post created at: {filename}")
    else:
        # Generate news article
        print("Generating news article...")
        article_data = news_generator.generate_article()
        
        if article_data:
            # Create news article without images for now
            print("Creating news article...")
            filename = article_data['filename']
            print(f"News article created at: {filename}")
    
    # Deploy
    print("Deploying...")
    deploy()

if __name__ == "__main__":
    main() 