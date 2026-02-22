"""
API Routes — Exam flow endpoints.
Student-only: start exam → answer questions → view results.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.api.schemas import (
    StartExamRequest, StartExamResponse,
    SubmitAnswerRequest, SubmitAnswerResponse,
    HintRequest, HintResponse,
    ExamSummaryResponse, ExamDetailResponse,
    TopicsResponse, TopicInfo,
    HealthResponse,
)
from app.services.exam_service import ExamService
from app.services.hint_service import HintService
from app.services.health_service import HealthService

router = APIRouter()

# Available topics with display info
TOPICS = [
    {"id": "python", "name": "Python", "icon": "🐍"},
    {"id": "oop", "name": "Object-Oriented Programming", "icon": "🏗️"},
    {"id": "data_structures", "name": "Data Structures", "icon": "📊"},
    {"id": "algorithms", "name": "Algorithms", "icon": "⚙️"},
    {"id": "sql", "name": "SQL & Databases", "icon": "🗄️"},
    {"id": "javascript", "name": "JavaScript", "icon": "🌐"},
    {"id": "java", "name": "Java", "icon": "☕"},
    {"id": "web_development", "name": "Web Development", "icon": "🖥️"},
]

# Available interview question categories
CATEGORIES = [
    {"id": "coding", "name": "Coding", "icon": "💻", "description": "Write functions and algorithms"},
    {"id": "concept", "name": "Concept", "icon": "📖", "description": "Explain technical concepts"},
    {"id": "debug", "name": "Debug", "icon": "🐛", "description": "Find and fix bugs in code"},
    {"id": "system_design", "name": "System Design", "icon": "🏛️", "description": "Design systems and architectures"},
    {"id": "behavioral", "name": "Behavioral", "icon": "🤝", "description": "Situational and teamwork questions"},
    {"id": "code_review", "name": "Code Review", "icon": "🔍", "description": "Review and improve given code"},
]

# Available exam modes
MODES = [
    {"id": "practice", "name": "Practice", "icon": "📝", "description": "Unlimited time, hints available", "has_timer": False, "has_hints": True},
    {"id": "timed", "name": "Timed Exam", "icon": "⏱️", "description": "Countdown timer, no hints", "has_timer": True, "has_hints": False},
    {"id": "mock", "name": "Mock Interview", "icon": "🎤", "description": "Real interview simulation with timer", "has_timer": True, "has_hints": True},
]


# --- Exam Endpoints ---

@router.post("/exam/start", response_model=StartExamResponse)
async def start_exam(request: StartExamRequest, db: Session = Depends(get_db)):
    """Start a new exam session. Generates the first question."""
    service = ExamService(db)
    try:
        result = await service.start_exam(
            topic=request.topic.value,
            difficulty=request.difficulty.value,
            num_questions=request.num_questions,
            question_type=request.question_type.value,
            category=request.category.value,
            mode=request.mode.value,
            time_limit_seconds=request.time_limit_seconds,
        )
        return StartExamResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start exam: {str(e)}")


@router.post("/exam/answer", response_model=SubmitAnswerResponse)
async def submit_answer(request: SubmitAnswerRequest, db: Session = Depends(get_db)):
    """Submit an answer to the current question. Returns grade + next question or summary."""
    service = ExamService(db)
    try:
        result = await service.submit_answer(
            exam_id=request.exam_id,
            answer=request.answer,
        )
        return SubmitAnswerResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Answer submission failed: {str(e)}")


@router.post("/exam/hint", response_model=HintResponse)
async def request_hint(request: HintRequest, db: Session = Depends(get_db)):
    """Request a hint for the current question. Reduces max score by 15% per hint."""
    service = HintService(db)
    try:
        result = await service.get_hint(exam_id=request.exam_id)
        return HintResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hint generation failed: {str(e)}")


@router.get("/exam/{exam_id}", response_model=ExamDetailResponse)
def get_exam(exam_id: str, db: Session = Depends(get_db)):
    """Get the full state of an exam session."""
    service = ExamService(db)
    try:
        result = service.get_exam(exam_id)
        return ExamDetailResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/exams", response_model=List[ExamSummaryResponse])
def list_exams(db: Session = Depends(get_db)):
    """List all exam sessions (history)."""
    service = ExamService(db)
    exams = service.get_all_exams()
    return [ExamSummaryResponse(**e) for e in exams]


# --- Topics ---

@router.get("/topics", response_model=TopicsResponse)
def get_topics():
    """Return available topics, difficulties, and question types."""
    return TopicsResponse(
        topics=[TopicInfo(**t) for t in TOPICS],
        difficulties=["easy", "medium", "hard"],
        question_types=["written", "multiple_choice"],
        categories=CATEGORIES,
        modes=MODES,
    )


# --- Health ---

@router.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """Check backend, database, and Ollama health."""
    service = HealthService(db)
    return await service.check_all()
