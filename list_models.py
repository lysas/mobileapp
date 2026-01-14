from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

try:
    print("Listing models...")
    for model in client.models.list(config={"page_size": 100}):
        if "generateContent" in model.supported_generation_methods:
            print(f"- {model.name}")
except Exception as e:
    print(f"Error: {e}")
