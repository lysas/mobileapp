import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

def test_user_image():
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    image_path = "C:/Users/Praveen Ramesh/.gemini/antigravity/brain/b2c96810-4e0a-4bcc-bc0b-e20975056072/uploaded_image_1768039513273.png"
    answer_map = {"1": "A", "2": "B", "3": "A"}

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    prompt = f"""
You are a strict MCQ answer evaluator.

The uploaded image contains ONLY a student’s final answers.
Answers may be handwritten or typed.

IMPORTANT RULES (DO NOT VIOLATE):

1. The student answers are written in simple formats such as:
   - "1 A"
   - "2 B"
   - "3 A"
   - "Q1: A"
   - "1) A"
   - Roman numerals like I, II must be treated as A, B respectively.

2. Ignore all descriptive text.
   Ignore explanations.
   Ignore sentences.
   ONLY extract final answer letters.

3. If an answer is missing, unclear, or unreadable:
   - Treat it as EMPTY ("").

4. DO NOT GUESS.
   DO NOT HALLUCINATE.
   DO NOT invent answers.

5. Evaluate answers strictly against the given Answer Key.

6. Scoring rules:
   - Correct answer = 1 mark
   - Wrong or missing answer = 0 mark

7. If the image is blank or answers cannot be extracted:
   - Return zero score
   - Leave student_answer as empty string ""

8. Output MUST be valid JSON ONLY.
   - No markdown
   - No explanation
   - No extra text

ANSWER KEY:
{json.dumps(answer_map, indent=2)}

STRICT OUTPUT FORMAT (MANDATORY):
{{
  "total_questions": number,
  "correct": number,
  "wrong": number,
  "score": number,
  "details": [
    {{
      "question": "1",
      "student_answer": "A",
      "correct_answer": "A",
      "result": "Correct"
    }}
  ]
}}
"""
    
    import logging
    logging.basicConfig(level=logging.DEBUG)
    print("Initializing Client...")
    try:
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        print("Reading Image...")
        image_path = "C:/Users/Praveen Ramesh/.gemini/antigravity/brain/b2c96810-4e0a-4bcc-bc0b-e20975056072/uploaded_image_1768039513273.png"
        answer_map = {"1": "A", "2": "B", "3": "A"}

        with open(image_path, "rb") as f:
            image_bytes = f.read()

        print("Calling Google API...")
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
                        types.Part.from_text(text=prompt)
                    ]
                )
            ],
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        print("API Response Received!")
        with open("test_result.json", "w") as f:
            f.write(response.text)
        print(response.text)
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    test_user_image()
