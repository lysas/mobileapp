from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print("Listing models...")
try:
    for m in client.models.list():
        print(f"Model: {m.name}")
        print(f"  Supported generation methods: {m.supported_generation_methods}")
except Exception as e:
    print(f"Error listing models: {e}")
