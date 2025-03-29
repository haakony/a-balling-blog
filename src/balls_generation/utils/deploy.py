"""Deployment utilities for the blog."""

import os
import subprocess
from datetime import datetime

from ..config.settings import BASE_DIR

def deploy():
    """Deploy the blog using Hugo."""
    try:
        # Change to the Hugo directory
        os.chdir(BASE_DIR)
        
        # Build the site
        print("Building site with Hugo...")
        subprocess.run(["hugo", "--minify"], check=True)
        
        # Deploy to GitHub Pages
        print("Deploying to GitHub Pages...")
        # First, commit any changes
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"Update content {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"], check=True)
        # Push to GitHub
        subprocess.run(["git", "push"], check=True)
        
        print("Deployment completed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"Error during deployment: {e}")
    except Exception as e:
        print(f"Unexpected error during deployment: {e}")
