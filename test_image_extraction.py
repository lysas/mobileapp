import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

image_path = r"C:/Users/Praveen Ramesh/.gemini/antigravity/brain/bdfe508f-21d1-4d56-bbd7-65edc4ad6c44/uploaded_image_1768366375056.jpg"

with open(image_path, "rb") as f:
    image_bytes = f.read()

prompt = """
You are an exam answer extractor.
Extract the selected option for each question from the image.
Return ONLY valid JSON in this format:
{
  "answers": {
    "1": "A",
    "2": "B",
    "3": "A"
  }
}
"""

try:
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            types.Part.from_text(text=prompt)
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )
    print(response.text)
except Exception as e:
    print(f"Error: {e}")
