"""Main entry point for the balls generation system."""

import os
from datetime import datetime

from .generators.story import StoryGenerator
from .generators.image import ImageGenerator
from .utils.deploy import deploy
from .config.settings import CONTENT_DIR

def create_blog_post(story_data, image_path, scene_image_path):
    """Create a new Hugo blog post with the generated content and image."""
    # Generate filename with current date
    current_date = datetime.now()
    date = current_date.strftime("%Y-%m-%d")
    timestamp = current_date.strftime("%H%M%S")
    
    # Use the title from story_data
    title = story_data['title']
    
    # Clean up the title
    title = title.replace('"', '').replace("'", '').replace('?', '').replace('!', '')
    title = ''.join(c for c in title[:60] if c.isalnum() or c.isspace() or c in '-')
    title = title.strip()
    
    # Create URL-friendly slug with timestamp to ensure uniqueness
    slug = title.lower().replace(' ', '-')
    filename = f"{CONTENT_DIR}/{date}-{slug}-{timestamp}.md"
    
    # Format the image paths correctly for Hugo
    if image_path:
        if image_path.startswith('images/'):
            image_path = image_path[7:]
        image_path = f"/images/{image_path}"
    
    if scene_image_path:
        if scene_image_path.startswith('images/'):
            scene_image_path = scene_image_path[7:]
        scene_image_path = f"/images/{scene_image_path}"
    
    # Create the front matter and content
    front_matter = f"""---
title: "{title}"
date: {date}
draft: false
---

"""
    
    # Add the main image using markdown syntax if we have one, wrapped in a link
    image_section = f"\n[![image]({image_path})]({date}-{slug}-{timestamp})\n" if image_path else ""
    
    # Get the first part of the story (up to the first period)
    first_part = story_data['story'].split('.')[0] + '.'
    
    # Create introduction section with the first part of the story
    intro_section = f"""

{first_part}

"""
    
    # Process the story to insert the scene image
    story_parts = story_data['story'].split('[SCENE]')
    story_with_image = story_parts[0]
    if len(story_parts) > 1 and scene_image_path:
        story_with_image += f"\n\n[![scene]({scene_image_path})]({date}-{slug}-{timestamp})\n\n" + story_parts[1]
    else:
        story_with_image = story_data['story']
    
    # Add the prompts section at the end
    prompts_section = f"""

---

### Generation Details

#### Story Generation Prompt
```text
Write a short, funny story about a {story_data['story'].split('.')[0].split()[0]}. 
The story should be around 300-400 words and be suitable for a blog post. 
Make it engaging and humorous.
```

#### Image Generation Prompt
```text
{story_data['image_prompt']}
```

#### Scene Image Generation Prompt
```text
{story_data['scene_prompt']}
```

#### Image Generation Settings
- Resolution: 768x768
- Steps: 30
- CFG: 7
- Sampler: DPM++ 2M
- Model: sd3_medium_incl_clips_t5xxlfp16.safetensors
"""
    
    # Write the content to the file
    with open(filename, "w", encoding="utf-8") as f:
        f.write(front_matter + image_section + intro_section + "\n<!--more-->\n\n" + story_with_image + prompts_section)
    
    return filename

def main():
    """Main entry point for the balls generation system."""
    print("Starting balls generation process...")
    
    # Initialize generators
    story_generator = StoryGenerator()
    image_generator = ImageGenerator()
    
    # Generate story
    print("Generating story...")
    story_data = story_generator.generate_story()
    
    if story_data:
        # Generate main image
        print("Generating main image...")
        image_path, _ = image_generator.generate_image(story_data['image_prompt'], "image")
        
        if image_path:
            # Generate scene image
            print("Generating scene image...")
            scene_image_path = image_generator.generate_image(story_data['scene_prompt'], "scene")[0]
            
            # Create blog post
            print("Creating blog post...")
            filename = create_blog_post(story_data, image_path, scene_image_path)
            print(f"Blog post created at: {filename}")
            
            # Deploy
            print("Deploying...")
            deploy()
        else:
            print("Failed to generate main image. Creating post without images...")
            filename = create_blog_post(story_data, "", "")
            print(f"Blog post created at: {filename}")
            
            print("Deploying...")
            deploy()
    else:
        print("Failed to generate story. Please check if Ollama is running.")

if __name__ == "__main__":
    main() 