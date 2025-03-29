"""Content creation utilities for blog posts and news articles."""

import os
from datetime import datetime

from ..config.settings import CONTENT_DIR

def create_news_article(article_data, image_path, scene_image_path):
    """Create a new Hugo news article with the generated content and image."""
    # Generate filename with current date
    current_date = datetime.now()
    date = current_date.strftime("%Y-%m-%d")
    timestamp = current_date.strftime("%H%M%S")
    
    # Use the title from article_data
    title = article_data['title']
    
    # Clean up the title
    title = title.replace('"', '').replace("'", '').replace('?', '').replace('!', '')
    title = ''.join(c for c in title[:60] if c.isalnum() or c.isspace() or c in '-')
    title = title.strip()
    
    # Create URL-friendly slug with timestamp to ensure uniqueness
    slug = title.lower().replace(' ', '-')
    filename = f"{CONTENT_DIR}/news/{date}-{slug}-{timestamp}.md"
    
    # Create news directory if it doesn't exist
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
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
categories: ["news", "{article_data['category']}"]
---

"""
    
    # Add the main image using markdown syntax if we have one, wrapped in a link
    image_section = f"\n[![image]({image_path})]({date}-{slug}-{timestamp})\n" if image_path else ""
    
    # Get the first part of the article (up to the first period)
    first_part = article_data['article'].split('.')[0] + '.'
    
    # Create introduction section with the first part of the article
    intro_section = f"""

{first_part}

"""
    
    # Process the article to insert the scene image
    article_parts = article_data['article'].split('[SCENE]')
    article_with_image = article_parts[0]
    if len(article_parts) > 1 and scene_image_path:
        article_with_image += f"\n\n[![scene]({scene_image_path})]({date}-{slug}-{timestamp})\n\n" + article_parts[1]
    else:
        article_with_image = article_data['article']
    
    # Add the prompts section at the end
    prompts_section = f"""

---

### Generation Details

#### Article Generation Prompt
```text
Write a humorous fake news article about a {article_data['article'].split('.')[0].split()[0]}. 
The article should be around 300-400 words and follow a typical news article structure.
```

#### Image Generation Prompt
```text
{article_data['image_prompt']}
```

#### Scene Image Generation Prompt
```text
{article_data['scene_prompt']}
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
        f.write(front_matter + image_section + intro_section + "\n<!--more-->\n\n" + article_with_image + prompts_section)
    
    return filename 