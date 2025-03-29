from balls_generation.llm_providers import get_llm_provider

# Get the provider
provider = get_llm_provider()

# Print which provider we're using
print(f"Using provider: {provider.__class__.__name__}")

# Try to generate some content
prompt = "Write a short, funny story about a tennis ball."
try:
    response = provider.generate_content(prompt)
    print("\nGenerated content:")
    print(response)
except Exception as e:
    print(f"Error: {e}") 