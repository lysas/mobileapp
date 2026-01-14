from fastapi import APIRouter, UploadFile, File, Form
import os, json, re, base64, io
from typing import List, Optional
from dotenv import load_dotenv

from google import genai
from google.genai import types
from google.genai import errors as genai_errors
import cohere
import fitz  # PyMuPDF

# --------------------------------------------------
# ENV + ROUTER
# --------------------------------------------------
load_dotenv()

router = APIRouter(prefix="/mcq", tags=["MCQ Evaluation"])

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# --------------------------------------------------
# HELPER: Normalize ANY answer key to {q: A/B/C/D}
# --------------------------------------------------
def normalize_answer_key(raw: str) -> dict:
    raw = raw.upper()

    # Roman numeral mapping
    raw = raw.replace("IV", "D").replace("III", "C").replace("II", "B").replace("I", "A")

    pairs = re.findall(r"(\d+)\s*[\)\-:\.]?\s*([A-D])", raw)
    return {q: a for q, a in pairs}


# --------------------------------------------------
# HELPER: Zero-score response
# --------------------------------------------------
def zero_score(answer_map: dict, error_msg: str):
    details = []
    for q, ans in answer_map.items():
        details.append({
            "question": q,
            "student_answer": "",
            "correct_answer": ans,
            "result": "Wrong"
        })

    return {
        "total_questions": len(details),
        "correct": 0,
        "wrong": len(details),
        "score": 0,
        "details": details,
        "error": error_msg
    }


# --------------------------------------------------
# HELPER: AI EXTRACTION ENGINE (REUSABLE)
# --------------------------------------------------
async def ai_extract_answers(files: List[UploadFile], custom_prompt: str) -> dict:
    """
    Common extraction logic for both student sheets and answer keys.
    Returns: {"1": "A", "2": "B", ...}
    """
    all_parts = []
    text_content = ""

    for file in files:
        if file.content_type not in ["image/jpeg", "image/png", "image/jpg", "application/pdf"]:
            continue
        
        file_bytes = await file.read()
        await file.seek(0)
        if not file_bytes or len(file_bytes) < 10:
            continue

        all_parts.append(types.Part.from_bytes(data=file_bytes, mime_type=file.content_type))

        if file.content_type == "application/pdf":
            try:
                doc = fitz.open(stream=file_bytes, filetype="pdf")
                for page in doc:
                    text_content += page.get_text()
            except: pass

    if not all_parts:
        return {}

    # 1. Gemini
    models = ["gemini-2.0-flash-exp", "gemini-1.5-flash", "gemini-1.5-flash-8b", "gemini-1.5-pro"]
    for model in models:
        try:
            response = client.models.generate_content(
                model=model,
                contents=[types.Content(role="user", parts=all_parts + [types.Part.from_text(text=custom_prompt)])],
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            if response.text:
                raw = response.text.strip().replace("```json", "").replace("```", "").strip()
                data = json.loads(raw)
                return data.get("answers", data) # Support both nested and flat responses
        except: continue

    # 2. Azure
    azure_key, azure_endpoint, azure_deployment = os.getenv("AZURE_OPENAI_KEY"), os.getenv("AZURE_OPENAI_ENDPOINT"), os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    if azure_key and azure_endpoint and azure_deployment:
        try:
            from openai import AzureOpenAI
            azure_client = AzureOpenAI(api_key=azure_key, api_version="2024-02-15-preview", azure_endpoint=azure_endpoint)
            msg_content = [{"type": "text", "text": custom_prompt}]
            for file in files:
                await file.seek(0)
                fb = await file.read()
                if file.content_type == "application/pdf":
                    doc = fitz.open(stream=fb, filetype="pdf")
                    for page in doc:
                        msg_content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64.b64encode(page.get_pixmap().tobytes('png')).decode('utf-8')}"}})
                else:
                    msg_content.append({"type": "image_url", "image_url": {"url": f"data:{file.content_type};base64,{base64.b64encode(fb).decode('utf-8')}"}})
            
            resp = azure_client.chat.completions.create(model=azure_deployment, messages=[{"role": "system", "content": "Extract MCQ answers. JSON only."}, {"role": "user", "content": msg_content}], response_format={"type": "json_object"})
            data = json.loads(resp.choices[0].message.content.strip())
            return data.get("answers", data)
        except: pass

    # 3. Cohere
    cohere_key = os.getenv("COHERE_API_KEY")
    if cohere_key and text_content:
        try:
            co = cohere.Client(cohere_key)
            resp = co.chat(model="command-r-plus-08-2024", message=custom_prompt + "\n\nTEXT:\n" + text_content, response_format={"type": "json_object"})
            data = json.loads(resp.text)
            return data.get("answers", data)
        except: pass

    return {}


# --------------------------------------------------
# MAIN API
# --------------------------------------------------
@router.post("/evaluate", summary="Evaluate MCQ Answer Sheets")
async def evaluate_mcq(
    student_answer_scripts: List[UploadFile] = File(
        ..., 
        description="Upload images/PDFs of student answers."
    ),
    type_answer_key_text: Optional[str] = Form(
        None, 
        description="Type answer key here.",
        openapi_examples={
            "Standard": {"value": "1 A, 2 B, 3 C"},
            "Dashed": {"value": "1-A, 2-B, 3-C"},
            "Roman": {"value": "1) i, 2) ii, 3) iii"}
        }
    ),
    upload_answer_key_file: Optional[UploadFile] = File(
        None, 
        description="Upload image/PDF of answer key."
    )
):

    # ---------- 1. Get Answer Key ----------
    answer_map = {}
    
    if upload_answer_key_file:
        # Validate format
        if upload_answer_key_file.content_type not in ["image/jpeg", "image/png", "image/jpg", "application/pdf"]:
            return {"error": "The answer key file format is not supported. Please upload a PDF or Image (JPG/PNG)."}

        key_prompt = """
Extract the MCQ Answer Key from this document.
Format: {"answers": {"1": "A", "2": "B", ...}}
Rules: Map i->A, ii->B, iii->C, iv->D. Output STRICT JSON.
"""
        extracted_key = await ai_extract_answers([upload_answer_key_file], key_prompt)
        if not extracted_key:
            return {"error": "We couldn't read the answers from your uploaded answer key file. Please ensure it is clear and contains a list of answers."}
        
        # Normalize keys/values to string uppercase
        answer_map = {str(k): str(v).upper() for k, v in extracted_key.items()}
    
    if not answer_map and type_answer_key_text:
        answer_map = normalize_answer_key(type_answer_key_text)

    if not answer_map:
        return {
            "total_questions": 0,
            "correct": 0,
            "wrong": 0,
            "score": 0,
            "details": [],
            "error": "Answer key missing. Please either type the answers in the text box or upload an answer key file."
        }

    # ---------- 2. Validate Student Scripts ----------
    valid_scripts = []
    for script in student_answer_scripts:
        if script.content_type not in ["image/jpeg", "image/png", "image/jpg", "application/pdf"]:
            return {"error": f"The file '{script.filename}' is not supported. Only PDF, JPG, and PNG are allowed."}
        
        # Check size (basic blank check)
        content = await script.read()
        await script.seek(0)
        if len(content) < 100:
            return {"error": f"The file '{script.filename}' appears to be empty or corrupted. Please upload a valid image or PDF."}
        valid_scripts.append(script)

    # ---------- 3. Extract Student Answers ----------
    student_prompt = """
You are an MCQ answer extractor.
Extract ONLY the selected option per question.
Rules: Map i->A, ii->B, iii->C, iv->D. Output STRICT JSON.
FORMAT: {"answers": {"1": "A", "2": "B"}}
"""
    ai_answers = await ai_extract_answers(valid_scripts, student_prompt)

    if not ai_answers:
        return zero_score(answer_map, "We couldn't detect any student answers on the uploaded scripts. Please check if the images are clear or if the student has marked their choices.")

    # ---------- 3. Python-side scoring ----------
    details = []
    correct = 0

    for q, correct_ans in answer_map.items():
        student_ans = str(ai_answers.get(q, "")).upper()

        if student_ans == correct_ans:
            correct += 1
            result = "Correct"
        else:
            result = "Wrong"

        details.append({
            "question": q,
            "student_answer": student_ans,
            "correct_answer": correct_ans,
            "result": result
        })

    return {
        "total_questions": len(answer_map),
        "correct": correct,
        "wrong": len(answer_map) - correct,
        "score": correct,
        "details": details
    }
