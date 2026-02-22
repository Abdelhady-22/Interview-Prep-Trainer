"""
QuestionService — Business logic for generating and managing questions.
Uses CrewAI crew to generate questions via LLM, with fallback to direct Ollama.
Supports 6 interview categories: coding, concept, debug, system_design, behavioral, code_review.
"""
import json
import re
import logging
from sqlalchemy.orm import Session

from app.agents.crew import grading_crew
from app.agents.question_generator_agent import get_prompt
from app.integrations.ollama_client import ollama_client
from app.repositories.question_repository import QuestionRepository
from app.config import settings

logger = logging.getLogger(__name__)

# Fallback system prompt — enforces structured JSON output
FALLBACK_SYSTEM = """You are a technical interview question generator.
You must respond with ONLY a valid JSON object.
No markdown. No explanation. No code blocks. Just the raw JSON object."""


class QuestionService:
    """Generates and stores interview-style programming questions."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = QuestionRepository(db)

    async def generate_question(
        self,
        topic: str,
        difficulty: str,
        question_type: str = "written",
        category: str = "concept",
        previous_questions: list = None,
    ) -> dict:
        """
        Generate a question via CrewAI, falling back to direct Ollama.
        Saves to DB and returns the question data.
        """
        prev = previous_questions or []

        # Try CrewAI crew first
        try:
            data = grading_crew.generate_question(
                topic=topic,
                difficulty=difficulty,
                question_type=question_type,
                category=category,
                previous_questions=prev,
            )
        except Exception as e:
            logger.warning(f"CrewAI question generation failed, using fallback: {e}")
            data = await self._fallback_generate(topic, difficulty, question_type, category, prev)

        # Save to DB
        db_data = {
            "topic": topic,
            "difficulty": difficulty,
            "question_type": question_type,
            "category": category,
            "question_text": data["question_text"],
            "correct_answer": data["correct_answer"],
            "explanation": data.get("explanation", ""),
            "options": data.get("options"),
        }
        question = self.repo.create(db_data)

        return {
            "id": str(question.id),
            "topic": topic,
            "difficulty": difficulty,
            "question_type": question_type,
            "category": category,
            "question_text": data["question_text"],
            "correct_answer": data["correct_answer"],
            "explanation": data.get("explanation", ""),
            "options": data.get("options"),
            "code_snippet": data.get("code_snippet"),
        }

    async def _fallback_generate(
        self,
        topic: str,
        difficulty: str,
        question_type: str,
        category: str,
        previous_questions: list,
    ) -> dict:
        """Direct Ollama fallback using category-specific prompts."""
        prompt = get_prompt(
            category=category,
            question_type=question_type,
            topic=topic,
            difficulty=difficulty,
            previous_questions=previous_questions,
        )

        for attempt in range(settings.MAX_RETRIES):
            try:
                raw = await ollama_client.generate(
                    prompt=prompt,
                    system=FALLBACK_SYSTEM,
                )
                data = _extract_json(raw)
                if "question_text" in data and "correct_answer" in data:
                    return data
            except Exception as e:
                logger.warning(f"Fallback generation attempt {attempt + 1} failed: {e}")

        raise ValueError("Failed to generate question after all retries")


def _extract_json(raw: str) -> dict:
    """Extract JSON from LLM output, handling markdown code blocks and extra text."""
    # Try code blocks first
    code_block = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
    text = code_block.group(1) if code_block else raw.strip()
    # Find the JSON object
    json_match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", text, re.DOTALL)
    if json_match:
        text = json_match.group(0)
    return json.loads(text)
