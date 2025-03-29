"""Content creation utilities for blog posts and news articles."""

import os
import re
from datetime import datetime

from ..config.settings import CONTENT_DIR

def clean_title(title: str) -> str:
    """Clean up a title for use in filenames and front matter."""
    # Remove any newlines and extra whitespace
    title = ' '.join(title.split())
    
    # Remove any special characters except spaces and hyphens
    title = re.sub(r'[^\w\s-]', '', title)
    
    # Replace spaces with hyphens
    title = title.replace(' ', '-')
    
    # Remove any multiple hyphens
    title = re.sub(r'-+', '-', title)
    
    # Remove leading/trailing hyphens
    title = title.strip('-')
    
    # Limit length to avoid overly long filenames
    return title[:50]

def clean_content(content: str) -> str:
    """Clean up story/article content by removing JSON artifacts and extra whitespace."""
    # Remove any JSON-like structures
    content = re.sub(r'\{[^}]+\}', '', content)
    
    # Remove any extra newlines (more than 2 consecutive)
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # Remove any leading/trailing whitespace
    content = content.strip()
    
    # Replace any remaining \n\n with actual newlines
    content = content.replace('\\n\\n', '\n\n')
    
    return content

def create_blog_post(story_data, image_path, scene_image_path):
    """Create a new Hugo blog post with the generated content and image."""
    # Generate filename with current date
    current_date = datetime.now()
    date = current_date.strftime("%Y-%m-%d")
    datetime_str = current_date.strftime("%Y-%m-%dT%H:%M:%S-00:00")
    timestamp = current_date.strftime("%H%M%S")
    
    # Clean up the title
    title = story_data['title']
    clean_title_for_file = clean_title(title)
    
    # Create URL-friendly slug with timestamp to ensure uniqueness
    filename = f"{CONTENT_DIR}/{date}-{clean_title_for_file}-{timestamp}.md"
    
    # Format the image paths correctly for Hugo
    if image_path:
        if image_path.startswith('images/'):
            image_path = image_path[7:]
        image_path = f"/images/{image_path}"
    
    if scene_image_path:
        if scene_image_path.startswith('images/'):
            scene_image_path = scene_image_path[7:]
        scene_image_path = f"/images/{scene_image_path}"
    
    # Get base tags from story data or use defaults
    base_tags = story_data.get('tags', ['story', 'humor', 'ball', 'fiction', 'funny', 'adventure', 'random', 'generated'])
    
    # Add model tags
    if 'openai' in story_data.get('models', []):
        base_tags.extend(['openai', 'gpt-4'])
    if 'dalle' in story_data.get('models', []):
        base_tags.append('dalle')
    
    # Create the front matter and content
    front_matter = f"""---
title: "{title}"
datetime: {datetime_str}
draft: false
categories: ["stories"]
tags: {base_tags}
---

"""
    
    # Add the main image using markdown syntax if we have one, wrapped in a link
    image_section = f"\n[![image]({image_path})]({date}-{clean_title_for_file}-{timestamp})\n" if image_path else ""
    
    # Clean and process the story content
    story_content = clean_content(story_data['story'])
    
    # Get the first part of the story (up to the first period)
    first_part = story_content.split('.')[0] + '.'
    
    # Create introduction section with the first part of the story
    intro_section = f"""

{first_part}

"""
    
    # Process the story to insert the scene image
    story_parts = story_content.split('[SCENE]')
    story_with_image = story_parts[0]
    if len(story_parts) > 1 and scene_image_path:
        story_with_image += f"\n\n[![scene]({scene_image_path})]({date}-{clean_title_for_file}-{timestamp})\n\n" + story_parts[1]
    else:
        story_with_image = story_content
    
    # Add the prompts section at the end
    prompts_section = f"""

---

### Generation Details

#### Story Generation Prompt
```text
Write a short, funny story about a {story_content.split('.')[0].split()[0]}. 
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
- Model: DALL-E 3
- Size: 1024x1024
- Quality: Standard
- Style: Natural
"""
    
    # Write the content to the file
    with open(filename, "w", encoding="utf-8") as f:
        f.write(front_matter + image_section + intro_section + "\n<!--more-->\n\n" + story_with_image + prompts_section)
    
    return filename

def create_news_article(article_data, image_path, scene_image_path):
    """Create a new Hugo news article with the generated content and image."""
    # Generate filename with current date
    current_date = datetime.now()
    date = current_date.strftime("%Y-%m-%d")
    datetime_str = current_date.strftime("%Y-%m-%dT%H:%M:%S-00:00")
    timestamp = current_date.strftime("%H%M%S")
    
    # Clean up the title
    title = article_data['title']
    clean_title_for_file = clean_title(title)
    
    # Create URL-friendly slug with timestamp to ensure uniqueness
    filename = f"{CONTENT_DIR}/news/{date}-{clean_title_for_file}-{timestamp}.md"
    
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
    
    # Get base tags from article data or use defaults
    base_tags = article_data.get('tags', ['news', 'humor', 'ball', 'satire', 'funny', 'generated', 'fake-news', 'parody', article_data['category']])
    
    # Add model tags
    if 'openai' in article_data.get('models', []):
        base_tags.extend(['openai', 'gpt-4'])
    if 'dalle' in article_data.get('models', []):
        base_tags.append('dalle')
    
    # Create the front matter and content
    front_matter = f"""---
title: "{title}"
datetime: {datetime_str}
draft: false
categories: ["news", "{article_data['category']}"]
tags: {base_tags}
---

"""
    
    # Add the main image using markdown syntax if we have one, wrapped in a link
    image_section = f"\n[![image]({image_path})]({date}-{clean_title_for_file}-{timestamp})\n" if image_path else ""
    
    # Clean and process the article content
    article_content = clean_content(article_data['article'])
    
    # Get the first part of the article (up to the first period)
    first_part = article_content.split('.')[0] + '.'
    
    # Create introduction section with the first part of the article
    intro_section = f"""

{first_part}

"""
    
    # Process the article to insert the scene image
    article_parts = article_content.split('[SCENE]')
    article_with_image = article_parts[0]
    if len(article_parts) > 1 and scene_image_path:
        article_with_image += f"\n\n[![scene]({scene_image_path})]({date}-{clean_title_for_file}-{timestamp})\n\n" + article_parts[1]
    else:
        article_with_image = article_content
    
    # Add the prompts section at the end
    prompts_section = f"""

---

### Generation Details

#### Article Generation Prompt
```text
Write a humorous fake news article about a {article_content.split('.')[0].split()[0]}. 
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
- Model: DALL-E 3
- Size: 1024x1024
- Quality: Standard
- Style: Natural
"""
    
    # Write the content to the file
    with open(filename, "w", encoding="utf-8") as f:
        f.write(front_matter + image_section + intro_section + "\n<!--more-->\n\n" + article_with_image + prompts_section)
    
    return filename 