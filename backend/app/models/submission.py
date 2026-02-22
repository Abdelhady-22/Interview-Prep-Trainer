import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, Boolean, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_type = Column(String(20), nullable=False, default="written")  # "written" or "multiple_choice"
    question = Column(Text, nullable=False)
    correct_answer = Column(Text, nullable=False)
    student_answer = Column(Text, nullable=False)
    options = Column(JSONB, nullable=True)  # MCQ only: {"A": "...", "B": "...", "C": "...", "D": "..."}
    score = Column(Float, nullable=False)
    max_score = Column(Integer, nullable=False, default=10)
    grade_letter = Column(String(2), nullable=False)
    passed = Column(Boolean, nullable=False)
    mistakes = Column(JSONB, nullable=True, default=list)
    strengths = Column(JSONB, nullable=True, default=list)
    feedback = Column(Text, nullable=True)
    recommendations = Column(JSONB, nullable=True, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
