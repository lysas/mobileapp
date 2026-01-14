# MCQ Evaluator

An AI-powered automated MCQ evaluation system that extracts student answers from multiple images or PDFs and generates instant scores and detailed reports.

## Overview

The MCQ Evaluator Backend provides a robust API for automated grading of Multiple Choice Questions (MCQs). It leverages a multi-tiered Generative AI stack (Google Gemini, Azure OpenAI, and Cohere) to process student answer sheets with high accuracy, handling various formats including checkboxes, handwritten letters, and roman numerals.

## Core Features

- Multi-File Support: Submit multiple images or multi-page PDFs in a single request for aggregated evaluation.
- Flexible Answer Keys: Provide the answer key as a text string, or upload an image/PDF file of the answer key for automatic extraction.
- Automated Answer Extraction: Reusable AI engine to detect student answers and answer keys across documents.
- Multi-tiered AI Fallback Strategy:
    - Primary: Google Gemini (2.0 Flash, 1.5 Flash, 1.5 Pro)
    - Secondary: Azure OpenAI (GPT-4o/Vision) with automatic PDF-to-Image conversion.
    - Final Fallback: Cohere (Command R+) using advanced text extraction from PDFs.
- Detailed Evaluation Results: Returns per-question accuracy, total score, and a breakdown of correct/wrong answers.
- Human-Readable Error Handling: Detailed, easy-to-understand error messages for unsupported file formats, empty files, missing keys, or unreadable images.
- Cross-Platform Compatibility: Specialized processing for various file types (.jpg, .png, .jpeg, .pdf).

## Backend Flow

1. Request Intake: Client sends a POST request to /mcq/evaluate with student images/PDFs and either a text answer key or an answer key file.
2. Key Extraction: If a file is provided, the AI extracted the answer key mapping. If text is provided, the backend normalizes it.
3. Batch Processing: All uploaded student files are validated and prepared for AI analysis.
4. AI Processing Pipeline: The system uses the multi-tiered fallback (Gemini -> Azure -> Cohere) to extract student answers.
5. Scoring Logic: A Python-based evaluation engine compares AI-extracted answers against the ground truth.
6. Response: A comprehensive JSON object is returned with scoring metrics and question-by-question results.

## Technical Stack

- Framework: FastAPI (High-performance Python web framework)
- AI Integration: Google GenAI SDK, Azure OpenAI, Cohere SDK
- Image/PDF Processing: PyMuPDF (fitz), Pillow, python-multipart
- Logic: Python 3.9+

## Project Structure

```text
backend/
├── app/
│   ├── main.py            # Entry point of the FastAPI application
│   ├── routers/
│   │   ├── mcq.py         # Main logic for MCQ evaluation and AI fallbacks
│   │   └── exam.py        # Sheet upload utilities
│   ├── evaluation/
│   │   ├── evaluate.py    # Core scoring algorithms
│   │   └── rubric.py      # Rubric definitions
│   ├── utils/
│   │   ├── gemini_client.py   # Dedicated Gemini API wrapper
│   │   └── ocr.py         # Advanced OCR logic
│   └── models.py          # Database models
├── .env                   # API Keys and Configuration
├── requirements.txt       # Project dependencies
└── run_all.py             # Script to start services
```

## Getting Started

### Prerequisites

- Python 3.9 or higher
- API Keys for Gemini, Azure (optional), and Cohere (optional)

### Installation

#### Windows (Powershell/CMD)

```powershell
# 1. Create a virtual environment
python -m venv venv

# 2. Activate the environment
.\venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and add your API Keys
```

#### Linux / macOS

```bash
# 1. Create a virtual environment
python3 -m venv venv

# 2. Activate the environment
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and add your API Keys
```

### Environment Variables

Create a .env file in the root directory and add the following:

```env
# Google Gemini (Primary)
GEMINI_API_KEY=your_gemini_key_here

# Azure OpenAI (Secondary Fallback)
AZURE_OPENAI_ENDPOINT=your_azure_endpoint
AZURE_OPENAI_KEY=your_azure_key
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name

# Cohere (Tertiary Fallback)
COHERE_API_KEY=your_cohere_key
```

### Running the Server

To start the development server with hot-reload:

Windows/Linux/macOS:
```bash
uvicorn app.main:app --reload
```
The API will be available at http://localhost:8000. You can access the interactive documentation at http://localhost:8000/docs.

## API Endpoints

### 1. Root Status
- Method: GET
- Path: /
- Response: {"status": "online"}

### 2. MCQ Evaluation
- Method: POST
- Path: /mcq/evaluate
- Body: multipart/form-data
    - student_answer_scripts: (List of student Image/PDF files)
    - type_answer_key_text: (Optional String, e.g., "1 A, 2 B")
    - upload_answer_key_file: (Optional Image/PDF file containing the key)
- Response:
```json
{
  "total_questions": 6,
  "correct": 5,
  "wrong": 1,
  "score": 5,
  "details": [
    {
      "question": "1",
      "student_answer": "A",
      "correct_answer": "A",
      "result": "Correct"
    },
    {
      "question": "2",
      "student_answer": "C",
      "correct_answer": "B",
      "result": "Wrong"
    }
  ]
}
```

---
Developed for Lysa Solutions
