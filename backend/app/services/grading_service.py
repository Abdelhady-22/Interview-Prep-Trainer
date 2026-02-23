"""
GradingService — Business logic orchestration for grading.
Branches on question_type: written (CrewAI crew) vs MCQ (deterministic + partial crew).
Includes single-prompt fallback mode.
"""
import json
import logging
from sqlalchemy.orm import Session

from app.config import settings
from app.agents.crew import grading_crew
from app.integrations.ollama_client import save_llm_response
from app.integrations.ollama_client import ollama_client
from app.repositories.submission_repository import SubmissionRepository
from app.api.schemas import GradeRequest, QuestionType

logger = logging.getLogger(__name__)

# Single-prompt fallback template
SINGLE_PROMPT_SYSTEM = """You are a strict exam grading assistant.
You must respond with ONLY a valid JSON object.
No markdown. No explanation. No code blocks. No extra text.
Just the raw JSON object and nothing else.

The JSON must follow this exact schema:
{
  "score": float between 0.0 and 10.0,
  "max_score": 10,
  "grade_letter": one of "A" "B" "C" "D" "F",
  "passed": boolean (true if score >= 5.0),
  "mistakes": [ { "type": string, "description": string } ],
  "strengths": [ string ],
  "feedback": string (main summary, 1-2 sentences),
  "recommendations": [
    {
      "topic": string,
      "action": string,
      "resource_type": one of "practice" "reading" "video" "exercise"
    }
  ],
  "encouragement": string (warm, personal, 1 sentence)
}

If the student answer is perfect, mistakes should be an empty array.
If no improvements needed, recommendations should be an empty array."""

SINGLE_PROMPT_USER = """Question: {question}
Correct Answer: {correct_answer}
Student Answer: {student_answer}

Grade this student answer. Return ONLY the JSON object."""

RETRY_ADDITION = "\n\nYour previous response was not valid JSON. Return ONLY the JSON object, nothing else."


class GradingService:
    """Orchestrates the grading flow."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = SubmissionRepository(db)

    async def grade(self, request: GradeRequest) -> dict:
        """
        Grade a submission based on question type and grading mode.
        Returns full result dict including encouragement.
        """
        if request.question_type == QuestionType.MULTIPLE_CHOICE:
            result = await self._grade_mcq(request)
        else:
            result = await self._grade_written(request)

        # Save to DB (without encouragement)
        db_data = {
            "question_type": request.question_type.value,
            "question": request.question,
            "correct_answer": request.correct_answer,
            "student_answer": request.student_answer,
            "options": request.options,
            "score": result["score"],
            "max_score": result["max_score"],
            "grade_letter": result["grade_letter"],
            "passed": result["passed"],
            "mistakes": result.get("mistakes", []),
            "strengths": result.get("strengths", []),
            "feedback": result.get("feedback", ""),
            "recommendations": result.get("recommendations", []),
        }
        self.repo.create(db_data)

        return result

    async def _grade_mcq(self, request: GradeRequest) -> dict:
        """Grade MCQ: deterministic score + CrewAI for feedback."""
        is_correct = request.student_answer == request.correct_answer
        score = 10.0 if is_correct else 0.0
        grade_letter = "A" if is_correct else "F"
        passed = is_correct

        if settings.GRADING_MODE == "crew":
            try:
                return grading_crew.grade_mcq(
                    question=request.question,
                    options=request.options,
                    correct_answer=request.correct_answer,
                    student_answer=request.student_answer,
                    score=score,
                    grade_letter=grade_letter,
                    passed=passed,
                )
            except Exception as e:
                logger.warning(f"CrewAI MCQ grading failed, using defaults: {e}")

        # Fallback: return deterministic result without LLM feedback
        return {
            "score": score,
            "max_score": 10,
            "grade_letter": grade_letter,
            "passed": passed,
            "mistakes": [] if is_correct else [{"type": "incorrect", "description": f"Selected {request.student_answer} instead of {request.correct_answer}"}],
            "strengths": ["Correct answer selected"] if is_correct else [],
            "feedback": "Correct!" if is_correct else f"The correct answer was {request.correct_answer}.",
            "recommendations": [],
            "encouragement": "Great job!" if is_correct else "Keep studying, you'll get it next time!",
        }

    async def _grade_written(self, request: GradeRequest) -> dict:
        """Grade written: full CrewAI crew or single-prompt fallback."""
        if settings.GRADING_MODE == "crew":
            try:
                return grading_crew.grade_written(
                    question=request.question,
                    correct_answer=request.correct_answer,
                    student_answer=request.student_answer,
                )
            except Exception as e:
                logger.warning(f"CrewAI written grading failed, falling back to single mode: {e}")

        # Single-prompt fallback
        return await self._grade_single_prompt(request)

    async def _grade_single_prompt(self, request: GradeRequest) -> dict:
        """Fallback: single prompt to Ollama with retry logic."""
        prompt = SINGLE_PROMPT_USER.format(
            question=request.question,
            correct_answer=request.correct_answer,
            student_answer=request.student_answer,
        )

        for attempt in range(settings.MAX_RETRIES):
            try:
                current_prompt = prompt
                if attempt == 1:
                    current_prompt += RETRY_ADDITION
                elif attempt == 2:
                    # Simplified prompt for last attempt
                    current_prompt = f"""Grade this answer. Return JSON only:
{{"score": <0-10>, "max_score": 10, "grade_letter": "<A/B/C/D/F>", "passed": <true/false>, "feedback": "<summary>", "encouragement": "<message>"}}

Question: {request.question}
Correct: {request.correct_answer}
Student: {request.student_answer}"""

                raw = await ollama_client.generate(
                    prompt=current_prompt,
                    system=SINGLE_PROMPT_SYSTEM,
                )

                # Try to extract JSON
                result = self._parse_llm_response(raw)
                if result:
                    return result

            except Exception as e:
                logger.warning(f"Single prompt attempt {attempt + 1} failed: {e}")

        # All retries exhausted
        raise ValueError("LLM failed to return valid response after all retries")

    def _parse_llm_response(self, raw: str) -> dict | None:
        """Parse LLM response into a valid grading result dict."""
        import re

        # Try code blocks first
        code_block = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
        text = code_block.group(1) if code_block else raw.strip()

        # Try to find JSON object
        json_match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", text, re.DOTALL)
        if json_match:
            text = json_match.group(0)

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return None

        # Validate required fields
        if "score" not in data:
            return None

        # Fill defaults
        score = float(data.get("score", 5.0))
        return {
            "score": max(0.0, min(10.0, score)),
            "max_score": 10,
            "grade_letter": data.get("grade_letter", self._score_to_grade(score)),
            "passed": data.get("passed", score >= 5.0),
            "mistakes": data.get("mistakes", []),
            "strengths": data.get("strengths", []),
            "feedback": data.get("feedback", ""),
            "recommendations": data.get("recommendations", []),
            "encouragement": data.get("encouragement", ""),
        }

    @staticmethod
    def _score_to_grade(score: float) -> str:
        if score >= 9.0:
            return "A"
        elif score >= 7.0:
            return "B"
        elif score >= 5.0:
            return "C"
        elif score >= 3.0:
            return "D"
        return "F"
