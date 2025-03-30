# A Balling site

An AI-powered content generation system that creates humorous stories and satirical news articles about various types of balls.

## Features

- Generates engaging stories and news articles about different types of balls
- Creates AI-generated images for both main content and scene illustrations
- Supports multiple LLM providers (OpenAI, Ollama)
- Supports multiple image generation providers (DALL-E, ComfyUI)
- Automatically formats content for Hugo static site

## Example Content

Here's an example of a generated story:

```markdown
---
title: "Great-Basketball"
date: 2025-03-30
draft: false
categories: ["story"]
tags: ['basketball', 'humor', 'kids', 'ollama', 'llama3.1:8b', 'comfyui', 'sd3_medium_incl_clips_t5xxlfp16.safetensors']
---

[![image](/images/comfyui-090916.png)](2025-03-30-great-basketball-090951)

It was a typical Tuesday afternoon at Springdale Elementary when chaos erupted in the school gym.

<!--more-->

It was a typical Tuesday afternoon at Springdale Elementary when chaos erupted in the school gym. The students were gathered for their weekly PE class, but all attention was focused on one thing a lone basketball that had somehow managed to roll out of bounds and onto the playground. The ball, which had been named Benny by the students, had a mind of its own. It began to roll around the playground, dodging chairs and leaping over puddles with ease. The kids watched in awe as Benny made his way down the slide, performing a perfect backwards flip at the bottom.

[![scene](/images/comfyui-090951.png)](2025-03-30-great-basketball-090951)

But little did they know, Benny had bigger plans. He rolled through the school gates and into the nearby park, where he met up with a group of mischievous squirrels. Together, they hatched a plan to infiltrate the schools cafeteria and steal all the cookies. The students followed Benny into the park, but by the time they arrived, the squirrel-ball alliance had already pulled off the heist. The kids were left standing in front of an empty cookie jar, surrounded by the remnants of their thieving friends. As it turned out, Benny was more than just a ball - he was a master thief with a taste for sweet treats.
```

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables in `.env`:
   ```
   OLLAMA_API_URL=http://your-ollama-server:11434
   OLLAMA_MODEL=llama3.1:8b
   OPENAI_API_KEY=your-openai-key
   IMAGE_PROVIDER=comfyui  # or dalle
   ```

## Usage

Run the generator:
```bash
python -m balls_generation
```

This will:
1. Generate a story or news article
2. Create images for the content
3. Format everything for Hugo
4. Deploy the content

## Configuration

The system can be configured through environment variables:

- `OLLAMA_API_URL`: URL of your Ollama server
- `OLLAMA_MODEL`: Model to use with Ollama
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_MODEL`: OpenAI model to use
- `USE_OPENAI`: Whether to use OpenAI instead of Ollama
- `IMAGE_PROVIDER`: Image generation provider (dalle or comfyui)
- `IMAGE_RESOLUTION`: Resolution for generated images
- `IMAGE_STEPS`: Number of steps for image generation
- `IMAGE_CFG`: CFG scale for image generation
- `IMAGE_SAMPLER`: Sampler to use for image generation
- `IMAGE_MODEL`: Model to use for image generation

## License

MIT License
