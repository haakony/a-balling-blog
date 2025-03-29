from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Print all relevant environment variables
print("Environment Variables:")
print(f"USE_OPENAI: {os.getenv('USE_OPENAI')}")
print(f"OPENAI_API_KEY: {'Set' if os.getenv('OPENAI_API_KEY') else 'Not Set'}")
print(f"OPENAI_MODEL: {os.getenv('OPENAI_MODEL')}")
print(f"OLLAMA_API_URL: {os.getenv('OLLAMA_API_URL')}")
print(f"OLLAMA_MODEL: {os.getenv('OLLAMA_MODEL')}") 