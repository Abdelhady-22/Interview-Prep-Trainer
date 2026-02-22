"""
SubmissionService — Manages retrieval of past submissions.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.repositories.submission_repository import SubmissionRepository
from app.models.submission import Submission


class SubmissionService:
    """Business logic for submission retrieval."""

    def __init__(self, db: Session):
        self.repo = SubmissionRepository(db)

    def get_all(self) -> List[Submission]:
        """Get all submissions ordered by newest first."""
        return self.repo.get_all()

    def get_by_id(self, submission_id: UUID) -> Optional[Submission]:
        """Get a single submission by ID."""
        return self.repo.get_by_id(submission_id)
