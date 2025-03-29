"""Image handling utilities."""

import os
import requests
from datetime import datetime
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def download_and_save_image(url: str, prefix: str = "image") -> Optional[str]:
    """Download an image from a URL and save it to the images directory.
    
    Args:
        url: The URL of the image to download
        prefix: Prefix for the filename (e.g., 'main', 'scene')
        
    Returns:
        Optional[str]: The path to the saved image, or None if download failed
    """
    try:
        # Create images directory if it doesn't exist
        images_dir = "static/images"
        os.makedirs(images_dir, exist_ok=True)
        
        # Generate a unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.png"
        filepath = os.path.join(images_dir, filename)
        
        # Download the image
        logger.info(f"Downloading image from {url}")
        response = requests.get(url)
        response.raise_for_status()
        
        # Save the image
        with open(filepath, "wb") as f:
            f.write(response.content)
        
        logger.info(f"Image saved to: {filepath}")
        return f"images/{filename}"  # Return path relative to static directory
        
    except Exception as e:
        logger.error(f"Error downloading image: {e}")
        return None 