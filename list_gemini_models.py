import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import google.generativeai as genai

api_key = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
genai.configure(api_key=api_key)

print("Available Gemini models for your API key:")
try:
    models = genai.list_models()
    for model in models:
        print(f"- {model.name} (supported methods: {model.supported_generation_methods})")
except Exception as e:
    print(f"Error listing models: {e}")
