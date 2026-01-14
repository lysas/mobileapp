from pydantic import BaseModel
from typing import Dict
from typing import List, Optional
class AnswerKeyCreate(BaseModel):
    subject: str
    answers: Dict[str, str]  # {"1":"A","2":"C"}
    total_marks: int
class MCQResult(BaseModel):
    question: str
    correct_answer: str
    detected_answer: Optional[str]
    status: str


class MCQEvaluationResponse(BaseModel):
    total_questions: int
    attempted: int
    correct: int
    score: int
    evaluation: List[MCQResult]