"""
Pydantic schemas for request validation and response serialization.
Covers: exam flow, grading, questions, topics, and health.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict
from uuid import UUID
from datetime import datetime
from enum import Enum


# --- Enums ---

class QuestionType(str, Enum):
    WRITTEN = "written"
    MULTIPLE_CHOICE = "multiple_choice"


class TopicEnum(str, Enum):
    PYTHON = "python"
    OOP = "oop"
    DATA_STRUCTURES = "data_structures"
    ALGORITHMS = "algorithms"
    SQL = "sql"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    WEB_DEVELOPMENT = "web_development"


class DifficultyEnum(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class CategoryEnum(str, Enum):
    CODING = "coding"
    CONCEPT = "concept"
    DEBUG = "debug"
    SYSTEM_DESIGN = "system_design"
    BEHAVIORAL = "behavioral"
    CODE_REVIEW = "code_review"


class ModeEnum(str, Enum):
    PRACTICE = "practice"
    TIMED = "timed"
    MOCK = "mock"


# Default per-question time limits (seconds) by mode
MODE_TIME_LIMITS = {
    "practice": None,     # No timer
    "timed": 300,         # 5 minutes per question
    "mock": 420,          # 7 minutes per question
}


class GradeLetter(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"


# --- Exam Request Schemas ---

class StartExamRequest(BaseModel):
    topic: TopicEnum
    difficulty: DifficultyEnum
    num_questions: int = Field(default=5, ge=1, le=20, description="Number of questions")
    question_type: QuestionType = QuestionType.WRITTEN
    category: CategoryEnum = CategoryEnum.CONCEPT
    mode: ModeEnum = ModeEnum.PRACTICE
    time_limit_seconds: Optional[int] = Field(None, ge=30, le=3600, description="Per-question time limit in seconds (null = use mode default)")


class SubmitAnswerRequest(BaseModel):
    exam_id: str = Field(..., description="UUID of the exam session")
    answer: str = Field(..., min_length=1, description="Student's answer")


class HintRequest(BaseModel):
    exam_id: str = Field(..., description="UUID of the exam session")


class HintResponse(BaseModel):
    hint: str
    hints_used: int
    score_penalty: float = Field(description="How much the max score is reduced")


# --- Exam Response Schemas ---

class QuestionResponse(BaseModel):
    id: str = ""
    question_text: str
    question_type: str = "written"
    category: str = "concept"
    options: Optional[Dict[str, str]] = None
    code_snippet: Optional[str] = None
    topic: str = ""
    difficulty: str = ""


class StartExamResponse(BaseModel):
    exam_id: str
    total_questions: int
    current_index: int
    mode: str = "practice"
    time_limit_seconds: Optional[int] = None
    question: QuestionResponse


class SubmitAnswerResponse(BaseModel):
    is_correct: bool
    score: float
    feedback: str = ""
    correct_answer: str
    encouragement: str = ""
    exam_completed: bool
    current_index: int = 0
    total_questions: int = 0
    score_so_far: float = 0.0
    next_question: Optional[QuestionResponse] = None
    exam_summary: Optional[dict] = None


class ExamSummaryResponse(BaseModel):
    exam_id: str
    topic: str
    difficulty: str
    question_type: str = "written"
    category: str = "concept"
    mode: str = "practice"
    total_questions: int
    score_total: float
    hints_used: int = 0
    status: str
    percentage: float = 0.0
    grade_letter: str = "F"
    created_at: Optional[str] = None
    completed_at: Optional[str] = None


class ExamDetailResponse(BaseModel):
    exam_id: str
    topic: str
    difficulty: str
    question_type: str = "written"
    category: str = "concept"
    mode: str = "practice"
    total_questions: int
    current_index: int
    score_total: float
    hints_used: int = 0
    status: str
    questions: List[dict] = []
    created_at: Optional[str] = None
    completed_at: Optional[str] = None


# --- Topic Info ---

class TopicInfo(BaseModel):
    id: str
    name: str
    icon: str = ""


class TopicsResponse(BaseModel):
    topics: List[TopicInfo]
    difficulties: List[str]
    question_types: List[str]
    categories: List[Dict[str, str]] = []
    modes: List[Dict] = []


# --- Legacy: Grade Request (kept for backwards compatibility) ---

class GradeRequest(BaseModel):
    question_type: QuestionType
    question: str = Field(..., min_length=1, description="The exam question")
    correct_answer: str = Field(..., min_length=1)
    student_answer: str = Field(..., min_length=1)
    options: Optional[Dict[str, str]] = Field(None)

    @field_validator("options")
    @classmethod
    def validate_options(cls, v, info):
        if info.data.get("question_type") == QuestionType.MULTIPLE_CHOICE:
            if not v:
                raise ValueError("Options are required for multiple choice questions")
            required_keys = {"A", "B", "C", "D"}
            if set(v.keys()) != required_keys:
                raise ValueError(f"Options must have exactly keys: {required_keys}")
        return v


# --- Health ---

class HealthResponse(BaseModel):
    backend: str = "ok"
    database: str = "ok"
    ollama: str = "ok"
