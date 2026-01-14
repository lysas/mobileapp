from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import json
import tempfile

load_dotenv()

# Initialize Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Models
PRIMARY_MODEL = "models/gemini-2.0-flash"
FALLBACK_MODEL = "models/gemini-1.5-flash-002"


async def extract_mcq_answers(file) -> dict:
    """
    Uses Gemini Vision to extract MCQ answers from image or PDF.
    RETURNS ONLY:
    {
      "1": "A",
      "2": "B"
    }
    """

    # Read uploaded file
    file_bytes = await file.read()

    # Save temporarily (Gemini prefers file upload)
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(file_bytes)
        temp_path = tmp.name

    # Upload file to Gemini
    uploaded_file = client.files.upload(path=temp_path)

    prompt = """
You are an exam evaluator.

The uploaded image or PDF contains MCQ answers marked by a student.

TASK:
- Detect ONLY the selected option for each question.
- Return ONLY the detected answers.

RULES:
- Output PURE JSON ONLY
- No markdown
- No explanation
- No nested structure
- Keys must be question numbers as strings
- Values must be A/B/C/D (uppercase)

OUTPUT FORMAT:
{
  "1": "A",
  "2": "B",
  "3": "C"
}
"""

    try:
        response = client.models.generate_content(
            model=PRIMARY_MODEL,
            contents=[prompt, uploaded_file],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0
            )
        )
    except Exception:
        response = client.models.generate_content(
            model=FALLBACK_MODEL,
            contents=[prompt, uploaded_file],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0
            )
        )

    # Get raw text
    text = response.text.strip()

    # Remove accidental markdown
    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()

    # Convert to dict
    detected_answers = json.loads(text)

    # Final safety filter (VERY IMPORTANT)
    clean_output = {}
    for k, v in detected_answers.items():
        if isinstance(v, str):
            clean_output[str(k)] = v.strip().upper()

    return clean_output
