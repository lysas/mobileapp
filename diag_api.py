import os
import sys
import json
from google import genai
from google.genai import errors as genai_errors
from dotenv import load_dotenv

load_dotenv()

def diagnostic():
    api_key = os.getenv("GEMINI_API_KEY")
    print(f"--- Diagnostic Start ---")
    print(f"Python Version: {sys.version}")
    print(f"API Key Found: {'Yes' if api_key else 'No'}")
    
    if not api_key:
        print("ERROR: GEMINI_API_KEY not found in environment. Check your .env file.")
        return

    print(f"Attempting to initialize GenAI Client...")
    try:
        client = genai.Client(api_key=api_key)
        print("Client initialized successfully.")
        
        print("Attempting to list models...")
        models_found = False
        try:
            for model in client.models.list(config={'page_size': 5}):
                print(f" - Found Model: {model.name}")
                models_found = True
            
            if not models_found:
                print("WARNING: No models returned from list call.")
            else:
                print("API Connectivity: OK")
        except genai_errors.ClientError as e:
            print(f"CLIENT ERROR during list: {e}")
        except genai_errors.ServerError as e:
            print(f"SERVER ERROR during list: {e}")
        except Exception as e:
            print(f"UNEXPECTED ERROR during list: {e}")

        print("\nAttempting a minimal text generation test (gemini-1.5-flash)...")
        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents="Say 'Hello Connectivity Test'"
            )
            print(f"Response: {response.text}")
            print("Generation: OK")
        except Exception as e:
            print(f"GENERATION ERROR: {e}")

    except Exception as e:
        print(f"CRITICAL INITIALIZATION ERROR: {e}")

    print(f"--- Diagnostic End ---")

if __name__ == "__main__":
    diagnostic()
