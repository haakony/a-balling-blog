from balls_generation.llm_providers import get_llm_provider

# Get the provider
provider = get_llm_provider()

# Print which provider we're using
print(f"Using provider: {provider.__class__.__name__}")

# Try to generate an image
prompt = "A photorealistic image of a tennis ball having a tea party with other sports balls, sitting at a tiny table with tiny teacups, soft lighting, high quality"
try:
    image_url = provider.generate_image(prompt)
    if image_url:
        print("\nGenerated image URL:")
        print(image_url)
    else:
        print("\nImage generation not supported or failed")
except Exception as e:
    print(f"Error: {e}") 