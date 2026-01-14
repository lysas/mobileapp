# app/utils/evaluation.py
# Check if file is empty
file_bytes = await file.read()
if file_bytes == b"":
    raise HTTPException(status_code=400, detail="Uploaded file is empty")

# Reset file pointer so Gemini can read it
await file.seek(0)

def normalize_gemini_answers(raw_answers: dict) -> dict:
    """
    Normalize Gemini output
    Example:
    {1: "b", "2": " C "} → {"1": "B", "2": "C"}
    """
    normalized = {}

    for q_no, ans in raw_answers.items():
        if ans:
            normalized[str(q_no)] = ans.strip().upper()

    return normalized


def evaluate_mcqs(detected_answers: dict, answer_key: dict) -> dict:
    evaluation = []
    score = 0
    attempted = 0

    for q_no, correct_ans in answer_key.items():
        detected = detected_answers.get(q_no)

        if detected is not None:
            attempted += 1

        if detected == correct_ans:
            status = "correct"
            score += 1
        elif detected is None:
            status = "unanswered"
        else:
            status = "wrong"

        evaluation.append({
            "question": q_no,
            "correct_answer": correct_ans,
            "detected_answer": detected,
            "status": status
        })

    return {
        "total_questions": len(answer_key),
        "attempted": attempted,
        "correct": score,
        "score": score,
        "evaluation": evaluation
    }
