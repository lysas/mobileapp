"""
Integrated Advanced OCR Pipeline
"""

import os
import io
import re
import json
from collections import defaultdict
from PIL import Image
import fitz  # PyMuPDF
import cv2
import numpy as np
from ultralytics import YOLO
from dotenv import load_dotenv
from google import genai
from google.genai.types import Part, Blob
import logging
from pathlib import Path
from pydantic import BaseModel, Field, RootModel
from typing import List, Dict, Optional, Any, Tuple
from dotenv import load_dotenv
load_dotenv()

# ------------------------------------------------------------------
# LOGGING
# ------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# ENV
# ------------------------------------------------------------------
load_dotenv()

# ==================================================================
# GEMINI CLIENT (SAFE + FIXED)
# ==================================================================

class MockResponse:
    def __init__(self, text, error=None):
        self.response = text
        self.error = error


class LocalGeminiClient:
    def __init__(self, model_name="gemini-1.5-flash-latest"):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment.")
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = model_name

    def generate_structured_json(self, contents, schema, call_type_for_logging=""):
        try:
            processed_contents = []

            for item in contents:
                if isinstance(item, Image.Image):
                    buf = io.BytesIO()
                    item.save(buf, format="PNG")

                    processed_contents.append(
                        Part(
                            inline_data=Blob(
                                data=buf.getvalue(),
                                mime_type="image/png"
                            )
                        )
                    )
                else:
                    processed_contents.append(item)

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=processed_contents,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": schema
                }
            )

            return MockResponse(response.text)

        except Exception as e:
            logger.error(f"Gemini API Error ({call_type_for_logging}): {e}")
            return MockResponse(None, error=str(e))


# ------------------------------------------------------------------
# INIT GEMINI
# ------------------------------------------------------------------
try:
    try:
        from centralised_llm.src.llms.gemini_genai_llm import GeminiGradingClient
        GRADING_CLIENT_INSTANCE = GeminiGradingClient(
            model_name="gemini-1.5-flash-latest"
        )
    except ImportError:
        GRADING_CLIENT_INSTANCE = LocalGeminiClient()

    logger.info("✅ Gemini Client initialized.")

except Exception as e:
    logger.critical(f"🚨 FAILED TO INITIALIZE GEMINI CLIENT: {e}")
    GRADING_CLIENT_INSTANCE = None

# ==================================================================
# YOLO
# ==================================================================

YOLO_MODEL_PATH = "grade/yolo/best2.pt"
YOLO_MODEL = None

if os.path.exists(YOLO_MODEL_PATH):
    try:
        logger.info("--- Loading YOLO Model ---")
        YOLO_MODEL = YOLO(YOLO_MODEL_PATH)
        YOLO_MODEL.predict(source=np.zeros((640, 640, 3), dtype=np.uint8), verbose=False)
        logger.info("--- YOLO ready ---")
    except Exception as e:
        logger.error(f"YOLO load error: {e}")
else:
    logger.warning("YOLO model not found. Diagram detection skipped.")

# ==================================================================
# PROMPT LOADER
# ==================================================================

def load_prompt(filename: str, prompt_dir: str = "ai_prompts") -> str:
    import yaml

    yaml_path = Path(prompt_dir) / filename
    txt_path = Path(prompt_dir) / filename.replace(".yaml", ".txt")

    if yaml_path.exists():
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data["prompt"] if isinstance(data, dict) else f.read()

    if txt_path.exists():
        with open(txt_path, "r", encoding="utf-8") as f:
            return f.read()

    raise FileNotFoundError(f"Prompt not found: {filename}")

# ==================================================================
# SCHEMAS
# ==================================================================

class PageScanResult(BaseModel):
    page_index: int
    page_number: int = 9999
    has_diagram: bool = False


class PageScanBatchResult(BaseModel):
    results: List[PageScanResult]


class EquationStep(BaseModel):
    step: int
    equation: str


class QuestionContent(BaseModel):
    text: Optional[str] = None
    equations: Optional[List[EquationStep]] = None
    tables: Optional[List[Dict[str, Any]]] = None
    bullets: Optional[List[str]] = None
    diagram: Optional[Dict[str, Any]] = None


class OutputModel(RootModel[Dict[str, QuestionContent]]):
    pass

# ==================================================================
# OCR HELPERS
# ==================================================================

def extract_images_from_pdf(pdf_path: str) -> List[Tuple[str, Image.Image]]:
    images = []
    doc = fitz.open(pdf_path)

    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=300)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        images.append((f"page_{i+1}", img))

    doc.close()
    return images


def images_to_pdf_bytes(images: List[Image.Image]) -> bytes:
    buf = io.BytesIO()
    images = [img.convert("RGB") for img in images]
    images[0].save(buf, format="PDF", save_all=True, append_images=images[1:])
    return buf.getvalue()

# ==================================================================
# GEMINI PDF CALL (FIXED)
# ==================================================================

def gemini_json_from_pdf(pdf_bytes: bytes, output_path: str, user_id: int) -> str:
    if not GRADING_CLIENT_INSTANCE:
        return json.dumps({"error": "Gemini not initialized"})

    prompt = load_prompt("ocr_extraction_prompt.yaml").format(
        output_path=output_path,
        user_id=user_id
    )

    pdf_part = Part(
        inline_data=Blob(
            data=pdf_bytes,
            mime_type="application/pdf"
        )
    )

    response = GRADING_CLIENT_INSTANCE.generate_structured_json(
        contents=[pdf_part, prompt],
        schema=OutputModel.model_json_schema(),
        call_type_for_logging="gemini_json_from_pdf"
    )

    if response.error:
        return json.dumps({"error": response.error})

    validated = OutputModel.model_validate_json(response.response)
    return validated.model_dump_json(indent=2)

# ==================================================================
# MAIN OCR PIPELINE
# ==================================================================

def process_answer_ocr(file_path, output_json_dir, output_images_dir, user_id):
    try:
        images = [img for _, img in extract_images_from_pdf(file_path)]
        pdf_bytes = images_to_pdf_bytes(images)

        raw_json = gemini_json_from_pdf(pdf_bytes, output_images_dir, user_id)

        os.makedirs(output_json_dir, exist_ok=True)
        json_path = os.path.join(output_json_dir, f"{user_id}_answers.json")

        with open(json_path, "w", encoding="utf-8") as f:
            f.write(raw_json)

        return {
            "success": True,
            "json_path": json_path,
            "pages_processed": len(images)
        }

    except Exception as e:
        logger.error(f"OCR failed: {e}", exc_info=True)
        return {"success": False, "error": str(e)}

# ==================================================================
# TEST ENTRY
# ==================================================================

if __name__ == "__main__":
    result = process_answer_ocr(
        "uploaded_sheets/sample.pdf",
        "output/json",
        "output/images",
        101
    )
    print(result)
