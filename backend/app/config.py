from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://grader:graderpass@db:5432/examgrader"

    # Ollama
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "qwen2.5:0.5b"

    # Grading
    MAX_RETRIES: int = 3
    GRADING_MODE: str = "crew"  # "crew" or "single"
    CREWAI_VERBOSE: bool = True

    # Optional per-agent model overrides
    GRADER_MODEL: Optional[str] = None
    FEEDBACK_MODEL: Optional[str] = None
    REVIEW_MODEL: Optional[str] = None
    GENERATOR_MODEL: Optional[str] = None

    # Exam settings
    DEFAULT_EXAM_QUESTIONS: int = 5

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
