from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"Key loaded (starts with): {api_key[:8]}...")

client = genai.Client(api_key=api_key)

print("\n--- Testing Generation ---")
try:
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents="Say hello in one sentence"
    )
    print("Gemini Response:")
    print(response.text)
except Exception as e:
    print("Generation Error:", e)
