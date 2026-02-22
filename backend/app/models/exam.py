"""
Exam model — tracks a full exam session (multiple questions).
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class Exam(Base):
    __tablename__ = "exams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic = Column(String(50), nullable=False)
    difficulty = Column(String(20), nullable=False)
    question_type = Column(String(20), nullable=False, default="written")
    category = Column(String(30), nullable=False, default="concept")
    mode = Column(String(20), nullable=False, default="practice")
    time_limit_seconds = Column(Integer, nullable=True)        # per-question timer (null = no limit)
    hints_used = Column(Integer, nullable=False, default=0)
    total_questions = Column(Integer, nullable=False, default=5)
    current_index = Column(Integer, nullable=False, default=0)
    score_total = Column(Float, nullable=False, default=0.0)
    status = Column(String(20), nullable=False, default="in_progress")
    # List of {question_id, question_text, correct_answer, student_answer, score, feedback, ...}
    questions = Column(JSONB, nullable=False, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)
