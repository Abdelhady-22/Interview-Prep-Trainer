"""
HintService — Generates contextual hints for the current question.
Hints reduce the maximum score for the question (penalty increases with each hint).
"""
import logging
import json
import re
from uuid import UUID
from sqlalchemy.orm import Session

from app.config import settings
from app.repositories.exam_repository import ExamRepository

logger = logging.getLogger(__name__)

# Hint penalty: each hint reduces max question score by this fraction
HINT_PENALTY_PER_HINT = 0.15  # 15% per hint
MAX_HINTS_PER_QUESTION = 3


def _build_hint_prompt(question_text: str, category: str, hint_number: int,
                       code_snippet: str = None) -> str:
    """Build a prompt to generate a hint for the given question."""
    snippet_block = ""
    if code_snippet:
        snippet_block = f"\n\nCode snippet:\n```\n{code_snippet}\n```"

    specificity = {
        1: "Give a GENERAL direction without revealing the answer. Point toward the right concept or approach.",
        2: "Give a MORE SPECIFIC hint. Mention the key technique, data structure, or principle involved.",
        3: "Give a VERY DIRECT hint that nearly reveals the answer, but let the student connect the final dots.",
    }

    level = specificity.get(hint_number, specificity[3])

    return f"""You are helping a student who is stuck on this interview question.

Question category: {category}
Question: {question_text}{snippet_block}

This is hint #{hint_number} of {MAX_HINTS_PER_QUESTION}.
{level}

Return ONLY a JSON object with this exact format:
{{"hint": "your hint text here"}}

No markdown. No code blocks. No extra text. ONLY the JSON object."""


class HintService:
    """Generates hints for exam questions."""

    def __init__(self, db: Session):
        self.db = db
        self.exam_repo = ExamRepository(db)

    async def get_hint(self, exam_id: str) -> dict:
        """
        Generate a hint for the current pending question.
        Returns: {"hint": str, "hints_used": int, "score_penalty": float}
        """
        exam = self.exam_repo.get_by_id(UUID(exam_id))
        if not exam:
            raise ValueError("Exam not found")
        if exam.status != "in_progress":
            raise ValueError("Exam is not in progress")

        # Only practice and mock modes allow hints
        if exam.mode == "timed":
            raise ValueError("Hints are not available in Timed Exam mode")

        questions = exam.questions or []

        # Find the current pending question
        pending = None
        pending_idx = None
        for i, q in enumerate(questions):
            if q.get("pending"):
                pending = q
                pending_idx = i
                break

        if not pending:
            raise ValueError("No pending question to hint on")

        # Track hints per question
        question_hints = pending.get("hints", [])
        hint_number = len(question_hints) + 1

        if hint_number > MAX_HINTS_PER_QUESTION:
            raise ValueError(f"Maximum {MAX_HINTS_PER_QUESTION} hints per question reached")

        # Generate the hint
        hint_text = await self._generate_hint(
            question_text=pending["question_text"],
            category=exam.category,
            hint_number=hint_number,
            code_snippet=pending.get("code_snippet"),
        )

        # Store the hint in the question data
        question_hints.append(hint_text)
        pending["hints"] = question_hints
        questions[pending_idx] = pending

        # Update exam
        total_hints = (exam.hints_used or 0) + 1
        self.exam_repo.update(exam, {
            "questions": questions,
            "hints_used": total_hints,
        })

        penalty = hint_number * HINT_PENALTY_PER_HINT

        return {
            "hint": hint_text,
            "hints_used": total_hints,
            "score_penalty": round(penalty, 2),
        }

    async def _generate_hint(self, question_text: str, category: str,
                             hint_number: int, code_snippet: str = None) -> str:
        """Generate a hint using the LLM."""
        import httpx

        prompt = _build_hint_prompt(question_text, category, hint_number, code_snippet)

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    f"{settings.OLLAMA_URL}/api/generate",
                    json={
                        "model": settings.OLLAMA_MODEL,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0.7},
                    },
                )
                response.raise_for_status()

            raw = response.json().get("response", "")

            # Try to extract JSON
            try:
                match = re.search(r'\{[^{}]*\}', raw, re.DOTALL)
                if match:
                    data = json.loads(match.group())
                    return data.get("hint", raw.strip())
            except (json.JSONDecodeError, AttributeError):
                pass

            # Fallback: return the raw text cleaned up
            return raw.strip()

        except Exception as e:
            logger.error(f"Hint generation failed: {e}")
            # Provide a generic fallback hint
            fallback_hints = {
                1: "Think about what data structure or approach would be most efficient here.",
                2: "Consider breaking the problem into smaller sub-problems.",
                3: "Review the key concepts related to this topic and look for edge cases.",
            }
            return fallback_hints.get(hint_number, "Review the fundamentals of this topic.")
