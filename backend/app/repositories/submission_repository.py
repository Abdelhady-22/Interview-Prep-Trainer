from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.submission import Submission


class SubmissionRepository:
    """Data access layer for submissions table."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> Submission:
        """Insert a new submission record."""
        submission = Submission(**data)
        self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)
        return submission

    def get_all(self) -> List[Submission]:
        """Retrieve all submissions ordered by created_at desc."""
        return (
            self.db.query(Submission)
            .order_by(Submission.created_at.desc())
            .all()
        )

    def get_by_id(self, submission_id: UUID) -> Optional[Submission]:
        """Retrieve a single submission by its ID."""
        return (
            self.db.query(Submission)
            .filter(Submission.id == submission_id)
            .first()
        )
