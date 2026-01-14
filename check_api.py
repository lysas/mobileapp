import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

def check_api():
    try:
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        for model in client.models.list(config={'page_size': 5}):
            print(f"Model: {model.name}")
        print("API connectivity verified.")
    except Exception as e:
        print(f"API Error: {e}")

if __name__ == "__main__":
    check_api()
