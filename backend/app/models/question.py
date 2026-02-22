"""
Question model — stores LLM-generated programming questions.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic = Column(String(50), nullable=False, index=True)
    difficulty = Column(String(20), nullable=False, index=True)
    question_type = Column(String(20), nullable=False, default="written")
    category = Column(String(30), nullable=False, default="concept")
    question_text = Column(Text, nullable=False)
    correct_answer = Column(Text, nullable=False)
    options = Column(JSONB, nullable=True)  # MCQ only: {"A": "...", ...}
    explanation = Column(Text, nullable=True)  # Why the answer is correct
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
