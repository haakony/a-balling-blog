# Balls Generation System

A Python package that generates humorous stories about various types of balls, complete with AI-generated illustrations.

## Features

- Generates unique stories about different types of balls using Ollama API
- Creates illustrations for stories using ComfyUI
- Automatically creates and deploys blog posts to Hugo
- Supports both main story images and scene-specific illustrations
- Clickable images that link to the full blog post

## Requirements

- Python 3.8 or higher
- Ollama API running locally (default: http://192.168.1.9:11434)
- ComfyUI running locally (default: http://192.168.1.9:7860)
- Hugo static site generator
- Git for deployment

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd balls-generation
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Generator

To generate a new story and blog post:

```bash
python -m balls_generation
```

### Setting up Cron Job

To run the generator daily at 8 AM:

```bash
0 8 * * * cd /path/to/balls-generation && /usr/bin/python3 -m balls_generation >> /path/to/balls-generation/cron.log 2>&1
```

## Configuration

The system can be configured by modifying `src/balls_generation/config/settings.py`:

- API URLs
- Directory paths
- Ball types
- Image generation settings

## Project Structure

```
balls-generation/
├── src/
│   └── balls_generation/
│       ├── __init__.py
│       ├── __main__.py
│       ├── config/
│       │   ├── __init__.py
│       │   └── settings.py
│       ├── generators/
│       │   ├── __init__.py
│       │   ├── story.py
│       │   └── image.py
│       └── utils/
│           ├── __init__.py
│           └── deploy.py
├── requirements.txt
└── README.md
```

## License

[Your chosen license]
