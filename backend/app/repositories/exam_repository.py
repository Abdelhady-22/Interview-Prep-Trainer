"""
Data access layer for the exams table.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.exam import Exam


class ExamRepository:
    """CRUD operations for Exam model."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> Exam:
        """Insert a new exam record."""
        exam = Exam(**data)
        self.db.add(exam)
        self.db.commit()
        self.db.refresh(exam)
        return exam

    def get_by_id(self, exam_id: UUID) -> Optional[Exam]:
        """Retrieve a single exam by its ID."""
        return (
            self.db.query(Exam)
            .filter(Exam.id == exam_id)
            .first()
        )

    def update(self, exam: Exam, data: dict) -> Exam:
        """Update an exam record with the given data."""
        for key, value in data.items():
            setattr(exam, key, value)
        self.db.commit()
        self.db.refresh(exam)
        return exam

    def get_all(self, status: str = None) -> List[Exam]:
        """Retrieve all exams, optionally filtered by status."""
        query = self.db.query(Exam)
        if status:
            query = query.filter(Exam.status == status)
        return query.order_by(Exam.created_at.desc()).all()
