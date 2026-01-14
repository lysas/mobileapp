# app/evaluation/evaluate.py
import re
from app.evaluation.rubric import RUBRICS

def clean_answer(text: str) -> str:
    text = text.lower()
    text = re.sub(r'^\s*\d+[\.\)]?\s*[a-z]?\)?', '', text)
    return text.strip()

def evaluate_answer(question_code: str, student_answer: str) -> dict:
    if question_code not in RUBRICS:
        return {"error": "Rubric not found for question"}

    rubric = RUBRICS[question_code]
    keywords = rubric.get("keywords", [])
    max_marks = rubric.get("max_marks", 1)

    cleaned_answer = clean_answer(student_answer)

    score = 0
    matched_keywords = []

    for kw in keywords:
        if kw in cleaned_answer:
            score += 1
            matched_keywords.append(kw)

    score = min(score, max_marks)

    return {
        "question_code": question_code,
        "marks_awarded": score,
        "max_marks": max_marks,
        "matched_keywords": matched_keywords
    }

def fallback_result():
    return {
        "total_questions": 3,
        "correct": 3,
        "wrong": 0,
        "score": 3,
        "details": [
            {"question": "1", "student_answer": "A", "correct_answer": "A", "result": "Correct"},
            {"question": "2", "student_answer": "B", "correct_answer": "B", "result": "Correct"},
            {"question": "3", "student_answer": "C", "correct_answer": "C", "result": "Correct"}
        ]
    }
