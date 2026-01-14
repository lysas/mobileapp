from sqlalchemy import Column, Integer, String, Text
from .database import Base

class AnswerKey(Base):
    __tablename__ = "answer_keys"
    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, nullable=False)
    answers = Column(Text, nullable=False)  # JSON string {"1":"A","2":"B"}
    total_marks = Column(Integer, nullable=False)
