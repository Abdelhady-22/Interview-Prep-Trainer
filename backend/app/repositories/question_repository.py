"""
Data access layer for the questions table.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.question import Question


class QuestionRepository:
    """CRUD operations for Question model."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> Question:
        """Insert a new question record."""
        question = Question(**data)
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return question

    def get_all(self, topic: str = None, difficulty: str = None) -> List[Question]:
        """Retrieve questions with optional filtering."""
        query = self.db.query(Question)
        if topic:
            query = query.filter(Question.topic == topic)
        if difficulty:
            query = query.filter(Question.difficulty == difficulty)
        return query.order_by(Question.created_at.desc()).all()

    def get_by_id(self, question_id: UUID) -> Optional[Question]:
        """Retrieve a single question by its ID."""
        return (
            self.db.query(Question)
            .filter(Question.id == question_id)
            .first()
        )
