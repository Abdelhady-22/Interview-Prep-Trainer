"""
ExamService — Business logic for the full exam flow.
Manages exam sessions: start → question → answer → grade → next → complete.
The correct_answer is always kept server-side in the exam's pending_question field.
"""
import logging
from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy.orm import Session

from app.config import settings
from app.services.question_service import QuestionService
from app.services.grading_service import GradingService
from app.repositories.exam_repository import ExamRepository
from app.api.schemas import GradeRequest, QuestionType, MODE_TIME_LIMITS
from app.services.hint_service import HINT_PENALTY_PER_HINT

logger = logging.getLogger(__name__)


class ExamService:
    """Orchestrates the automated exam flow."""

    def __init__(self, db: Session):
        self.db = db
        self.exam_repo = ExamRepository(db)
        self.question_service = QuestionService(db)
        self.grading_service = GradingService(db)

    async def start_exam(
        self,
        topic: str,
        difficulty: str,
        num_questions: int = None,
        question_type: str = "written",
        category: str = "concept",
        mode: str = "practice",
        time_limit_seconds: int = None,
    ) -> dict:
        """
        Start a new exam session.
        Generates the first question and stores it (with correct_answer) server-side.
        """
        num_q = num_questions or settings.DEFAULT_EXAM_QUESTIONS

        # Generate first question
        question = await self.question_service.generate_question(
            topic=topic,
            difficulty=difficulty,
            question_type=question_type,
            category=category,
            previous_questions=[],
        )

        # Resolve time limit: explicit value > mode default > None
        resolved_time = time_limit_seconds or MODE_TIME_LIMITS.get(mode)

        # Create exam record with the pending question stored server-side
        exam_data = {
            "topic": topic,
            "difficulty": difficulty,
            "question_type": question_type,
            "category": category,
            "mode": mode,
            "time_limit_seconds": resolved_time,
            "hints_used": 0,
            "total_questions": num_q,
            "current_index": 0,
            "score_total": 0.0,
            "status": "in_progress",
            "questions": [{
                "pending": True,
                "question_text": question["question_text"],
                "correct_answer": question["correct_answer"],
                "explanation": question.get("explanation", ""),
                "options": question.get("options"),
                "code_snippet": question.get("code_snippet"),
            }],
        }
        exam = self.exam_repo.create(exam_data)

        return {
            "exam_id": str(exam.id),
            "total_questions": num_q,
            "current_index": 1,
            "mode": mode,
            "time_limit_seconds": resolved_time,
            "question": _sanitize_question(question, question_type, category),
        }

    async def submit_answer(self, exam_id: str, answer: str) -> dict:
        """
        Submit an answer for the current question.
        Retrieves the correct_answer from the server-side pending question,
        grades it, saves the result, and generates the next question (or finalizes).
        """
        exam = self.exam_repo.get_by_id(UUID(exam_id))
        if not exam:
            raise ValueError("Exam not found")
        if exam.status == "completed":
            raise ValueError("Exam already completed")

        questions_list = list(exam.questions) if exam.questions else []

        # Find the pending question (the last one with pending=True)
        pending_q = None
        pending_idx = -1
        for i in range(len(questions_list) - 1, -1, -1):
            if questions_list[i].get("pending"):
                pending_q = questions_list[i]
                pending_idx = i
                break

        if pending_q is None:
            raise ValueError("No pending question found for this exam")

        question_text = pending_q["question_text"]
        correct_answer = pending_q["correct_answer"]
        options = pending_q.get("options")
        q_type = exam.question_type

        # Grade the answer
        grade_result = await self._grade_answer(
            question=question_text,
            correct_answer=correct_answer,
            student_answer=answer,
            question_type=q_type,
            options=options,
        )

        score = grade_result.get("score", 0.0)
        is_correct = grade_result.get("passed", False)

        # Apply hint penalty: reduce score by 15% per hint used on this question
        question_hints = pending_q.get("hints", [])
        if question_hints:
            penalty_fraction = len(question_hints) * HINT_PENALTY_PER_HINT
            score = round(score * max(0, 1 - penalty_fraction), 1)

        # Update the pending question record with the student's answer and grade
        questions_list[pending_idx] = {
            "pending": False,
            "question_text": question_text,
            "correct_answer": correct_answer,
            "explanation": pending_q.get("explanation", ""),
            "options": options,
            "hints": question_hints,
            "student_answer": answer,
            "score": score,
            "is_correct": is_correct,
            "feedback": grade_result.get("feedback", ""),
            "encouragement": grade_result.get("encouragement", ""),
        }

        new_index = exam.current_index + 1
        new_score = exam.score_total + score
        exam_completed = new_index >= exam.total_questions

        update_data = {
            "questions": questions_list,
            "current_index": new_index,
            "score_total": new_score,
        }

        if exam_completed:
            update_data["status"] = "completed"
            update_data["completed_at"] = datetime.now(timezone.utc)

        # Build response
        response = {
            "is_correct": is_correct,
            "score": score,
            "feedback": grade_result.get("feedback", ""),
            "correct_answer": correct_answer,
            "encouragement": grade_result.get("encouragement", ""),
            "exam_completed": exam_completed,
            "current_index": new_index + 1 if not exam_completed else new_index,
            "total_questions": exam.total_questions,
            "score_so_far": new_score,
        }

        if not exam_completed:
            # Generate next question
            prev_questions = [
                q["question_text"] for q in questions_list if not q.get("pending")
            ]
            next_question = await self.question_service.generate_question(
                topic=exam.topic,
                difficulty=exam.difficulty,
                question_type=exam.question_type,
                category=exam.category,
                previous_questions=prev_questions,
            )

            # Store the next pending question server-side
            questions_list.append({
                "pending": True,
                "question_text": next_question["question_text"],
                "correct_answer": next_question["correct_answer"],
                "explanation": next_question.get("explanation", ""),
                "options": next_question.get("options"),
                "code_snippet": next_question.get("code_snippet"),
            })
            update_data["questions"] = questions_list

            response["next_question"] = _sanitize_question(next_question, exam.question_type, exam.category)
        else:
            # Return exam summary
            answered = [q for q in questions_list if not q.get("pending")]
            response["exam_summary"] = self._build_summary(exam, answered, new_score)

        self.exam_repo.update(exam, update_data)

        return response

    async def _grade_answer(
        self,
        question: str,
        correct_answer: str,
        student_answer: str,
        question_type: str,
        options: dict = None,
    ) -> dict:
        """Grade a single answer using the existing grading infrastructure."""
        if question_type == "multiple_choice":
            is_correct = student_answer.strip().upper() == correct_answer.strip().upper()
            score = 10.0 if is_correct else 0.0
            return {
                "score": score,
                "passed": is_correct,
                "feedback": "Correct!" if is_correct else f"The correct answer was {correct_answer}.",
                "encouragement": "Great job! 🎉" if is_correct else "Keep studying, you'll get there! 💪",
            }
        else:
            # Use single-prompt grading for written answers
            try:
                q_type = QuestionType.WRITTEN
                grade_request = GradeRequest(
                    question_type=q_type,
                    question=question,
                    correct_answer=correct_answer,
                    student_answer=student_answer,
                    options=None,
                )
                result = await self.grading_service._grade_single_prompt(grade_request)
                return result
            except Exception as e:
                logger.warning(f"Grading failed, using basic comparison: {e}")
                similarity = _basic_similarity(student_answer, correct_answer)
                score = round(similarity * 10, 1)
                return {
                    "score": score,
                    "passed": score >= 5.0,
                    "feedback": f"Your answer received a score of {score}/10.",
                    "encouragement": "Keep learning and improving! 📚",
                }

    def get_exam(self, exam_id: str) -> dict:
        """Get full exam state."""
        exam = self.exam_repo.get_by_id(UUID(exam_id))
        if not exam:
            raise ValueError("Exam not found")

        return {
            "exam_id": str(exam.id),
            "topic": exam.topic,
            "difficulty": exam.difficulty,
            "question_type": exam.question_type,
            "category": exam.category,
            "mode": exam.mode,
            "total_questions": exam.total_questions,
            "current_index": exam.current_index,
            "score_total": exam.score_total,
            "hints_used": exam.hints_used or 0,
            "status": exam.status,
            "questions": [
                _redact_question(q) for q in (exam.questions or [])
            ],
            "created_at": exam.created_at.isoformat() if exam.created_at else None,
            "completed_at": exam.completed_at.isoformat() if exam.completed_at else None,
        }

    def get_all_exams(self) -> list:
        """Get all exam sessions."""
        exams = self.exam_repo.get_all()
        return [
            {
                "exam_id": str(e.id),
                "topic": e.topic,
                "difficulty": e.difficulty,
                "question_type": e.question_type,
                "category": e.category,
                "mode": e.mode,
                "total_questions": e.total_questions,
                "score_total": e.score_total,
                "hints_used": e.hints_used or 0,
                "status": e.status,
                "percentage": round((e.score_total / (e.total_questions * 10)) * 100, 1)
                    if e.total_questions > 0 else 0,
                "grade_letter": _score_to_grade(
                    (e.score_total / (e.total_questions * 10)) * 100
                    if e.total_questions > 0 else 0
                ),
                "created_at": e.created_at.isoformat() if e.created_at else None,
                "completed_at": e.completed_at.isoformat() if e.completed_at else None,
            }
            for e in exams
        ]

    def _build_summary(self, exam, questions_list: list, total_score: float) -> dict:
        """Build exam summary response."""
        max_score = exam.total_questions * 10
        percentage = round((total_score / max_score) * 100, 1) if max_score > 0 else 0

        return {
            "exam_id": str(exam.id),
            "topic": exam.topic,
            "difficulty": exam.difficulty,
            "total_questions": exam.total_questions,
            "total_score": total_score,
            "max_score": max_score,
            "percentage": percentage,
            "grade_letter": _score_to_grade(percentage),
            "passed": percentage >= 50.0,
            "questions": [
                {
                    "question_text": q.get("question_text", ""),
                    "correct_answer": q.get("correct_answer", ""),
                    "student_answer": q.get("student_answer", ""),
                    "score": q.get("score", 0),
                    "is_correct": q.get("is_correct", False),
                    "feedback": q.get("feedback", ""),
                }
                for q in questions_list
            ],
        }


def _sanitize_question(question: dict, question_type: str, category: str = "concept") -> dict:
    """Remove the correct answer from question data sent to frontend."""
    result = {
        "question_text": question.get("question_text", ""),
        "question_type": question_type,
        "category": category,
        "topic": question.get("topic", ""),
        "difficulty": question.get("difficulty", ""),
    }
    if question_type == "multiple_choice" and question.get("options"):
        result["options"] = question["options"]
    if question.get("code_snippet"):
        result["code_snippet"] = question["code_snippet"]
    return result


def _redact_question(q: dict) -> dict:
    """Redact pending questions for client view, show answered ones."""
    if q.get("pending"):
        return {
            "pending": True,
            "question_text": q.get("question_text", ""),
            "options": q.get("options"),
        }
    return {
        "pending": False,
        "question_text": q.get("question_text", ""),
        "student_answer": q.get("student_answer", ""),
        "correct_answer": q.get("correct_answer", ""),
        "score": q.get("score", 0),
        "is_correct": q.get("is_correct", False),
        "feedback": q.get("feedback", ""),
    }


def _score_to_grade(percentage: float) -> str:
    """Convert percentage to grade letter."""
    if percentage >= 90:
        return "A"
    elif percentage >= 70:
        return "B"
    elif percentage >= 50:
        return "C"
    elif percentage >= 30:
        return "D"
    return "F"


def _basic_similarity(text1: str, text2: str) -> float:
    """Very basic word overlap similarity as last fallback."""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    if not words1 or not words2:
        return 0.0
    overlap = words1 & words2
    return len(overlap) / max(len(words1), len(words2))
