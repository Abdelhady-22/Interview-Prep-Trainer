"""
GradingCrew — Orchestrates the multi-agent grading flow using CrewAI.
Supports both written (3 agents) and MCQ (2 agents, score is deterministic).
"""
import json
import logging
import re
from crewai import Agent, Task, Crew, Process, LLM

from app.config import settings
from app.agents.grader_agent import (
    GRADER_ROLE, GRADER_GOAL, GRADER_BACKSTORY,
    GRADER_TASK_DESCRIPTION, GRADER_EXPECTED_OUTPUT,
)
from app.agents.feedback_agent import (
    FEEDBACK_ROLE, FEEDBACK_GOAL, FEEDBACK_BACKSTORY,
    FEEDBACK_TASK_WRITTEN, FEEDBACK_TASK_MCQ, FEEDBACK_EXPECTED_OUTPUT,
)
from app.agents.review_agent import (
    REVIEW_ROLE, REVIEW_GOAL, REVIEW_BACKSTORY,
    REVIEW_TASK_DESCRIPTION, REVIEW_EXPECTED_OUTPUT,
)
from app.agents.question_generator_agent import (
    GENERATOR_ROLE, GENERATOR_GOAL, GENERATOR_BACKSTORY,
    GENERATOR_EXPECTED_OUTPUT, get_prompt,
)

logger = logging.getLogger(__name__)


def _build_llm(model_override: str = None) -> LLM:
    """Build a CrewAI LLM instance pointing to Ollama."""
    model = model_override or settings.OLLAMA_MODEL
    return LLM(
        model=f"ollama/{model}",
        base_url=settings.OLLAMA_BASE_URL,
    )


def _extract_json(text: str) -> dict:
    """Extract a JSON object from LLM text output, handling markdown fences."""
    # Try to find JSON in code blocks first
    code_block = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if code_block:
        return json.loads(code_block.group(1))

    # Try to find raw JSON object
    json_match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", text, re.DOTALL)
    if json_match:
        return json.loads(json_match.group(0))

    # Last resort: try the whole text
    return json.loads(text.strip())


class GradingCrew:
    """Orchestrates multi-agent grading using CrewAI."""

    def __init__(self):
        self.verbose = settings.CREWAI_VERBOSE

    def grade_written(self, question: str, correct_answer: str, student_answer: str) -> dict:
        """
        Run full 3-agent crew for written questions.
        Returns combined grading result dict.
        """
        grader_llm = _build_llm(settings.GRADER_MODEL)
        feedback_llm = _build_llm(settings.FEEDBACK_MODEL)
        review_llm = _build_llm(settings.REVIEW_MODEL)

        # --- Agents ---
        grader = Agent(
            role=GRADER_ROLE,
            goal=GRADER_GOAL,
            backstory=GRADER_BACKSTORY,
            llm=grader_llm,
            verbose=self.verbose,
            allow_delegation=False,
        )

        feedback_provider = Agent(
            role=FEEDBACK_ROLE,
            goal=FEEDBACK_GOAL,
            backstory=FEEDBACK_BACKSTORY,
            llm=feedback_llm,
            verbose=self.verbose,
            allow_delegation=False,
        )

        reviewer = Agent(
            role=REVIEW_ROLE,
            goal=REVIEW_GOAL,
            backstory=REVIEW_BACKSTORY,
            llm=review_llm,
            verbose=self.verbose,
            allow_delegation=False,
        )

        # --- Tasks ---
        grading_task = Task(
            description=GRADER_TASK_DESCRIPTION.format(
                question=question,
                correct_answer=correct_answer,
                student_answer=student_answer,
            ),
            expected_output=GRADER_EXPECTED_OUTPUT,
            agent=grader,
        )

        # Feedback task will get grading context
        feedback_task = Task(
            description=FEEDBACK_TASK_WRITTEN.format(
                question=question,
                correct_answer=correct_answer,
                student_answer=student_answer,
                score="{score}",  # Placeholder, filled after grading
                grade_letter="{grade_letter}",
            ),
            expected_output=FEEDBACK_EXPECTED_OUTPUT,
            agent=feedback_provider,
            context=[grading_task],
        )

        review_task = Task(
            description=REVIEW_TASK_DESCRIPTION.format(
                question=question,
                student_answer=student_answer,
                score="{score}",
                grade_letter="{grade_letter}",
                passed="{passed}",
                feedback="{feedback}",
            ),
            expected_output=REVIEW_EXPECTED_OUTPUT,
            agent=reviewer,
            context=[grading_task, feedback_task],
        )

        # --- Crew ---
        crew = Crew(
            agents=[grader, feedback_provider, reviewer],
            tasks=[grading_task, feedback_task, review_task],
            process=Process.sequential,
            verbose=self.verbose,
        )

        result = crew.kickoff()

        # Parse results from each task
        return self._combine_results(grading_task, feedback_task, review_task)

    def grade_mcq(
        self,
        question: str,
        options: dict,
        correct_answer: str,
        student_answer: str,
        score: float,
        grade_letter: str,
        passed: bool,
    ) -> dict:
        """
        Run 2-agent crew for MCQ (score is pre-computed).
        FeedbackAgent + ReviewAgent only.
        """
        feedback_llm = _build_llm(settings.FEEDBACK_MODEL)
        review_llm = _build_llm(settings.REVIEW_MODEL)

        result_text = "CORRECT" if passed else "INCORRECT"

        # --- Agents ---
        feedback_provider = Agent(
            role=FEEDBACK_ROLE,
            goal=FEEDBACK_GOAL,
            backstory=FEEDBACK_BACKSTORY,
            llm=feedback_llm,
            verbose=self.verbose,
            allow_delegation=False,
        )

        reviewer = Agent(
            role=REVIEW_ROLE,
            goal=REVIEW_GOAL,
            backstory=REVIEW_BACKSTORY,
            llm=review_llm,
            verbose=self.verbose,
            allow_delegation=False,
        )

        # --- Tasks ---
        feedback_task = Task(
            description=FEEDBACK_TASK_MCQ.format(
                question=question,
                option_a=options.get("A", ""),
                option_b=options.get("B", ""),
                option_c=options.get("C", ""),
                option_d=options.get("D", ""),
                correct_answer=correct_answer,
                correct_text=options.get(correct_answer, ""),
                student_answer=student_answer,
                student_text=options.get(student_answer, ""),
                result=result_text,
            ),
            expected_output=FEEDBACK_EXPECTED_OUTPUT,
            agent=feedback_provider,
        )

        review_task = Task(
            description=REVIEW_TASK_DESCRIPTION.format(
                question=question,
                student_answer=f"{student_answer}) {options.get(student_answer, '')}",
                score=score,
                grade_letter=grade_letter,
                passed=passed,
                feedback="{feedback}",
            ),
            expected_output=REVIEW_EXPECTED_OUTPUT,
            agent=reviewer,
            context=[feedback_task],
        )

        # --- Crew ---
        crew = Crew(
            agents=[feedback_provider, reviewer],
            tasks=[feedback_task, review_task],
            process=Process.sequential,
            verbose=self.verbose,
        )

        crew.kickoff()

        # Parse feedback + review results
        return self._combine_mcq_results(feedback_task, review_task, score, grade_letter, passed)

    def _combine_results(self, grading_task, feedback_task, review_task) -> dict:
        """Combine outputs from all 3 tasks into a single result dict."""
        result = {
            "score": 5.0,
            "max_score": 10,
            "grade_letter": "C",
            "passed": True,
            "mistakes": [],
            "strengths": [],
            "feedback": "",
            "recommendations": [],
            "encouragement": "",
        }

        # Parse grading result
        try:
            grading_data = _extract_json(str(grading_task.output))
            result["score"] = float(grading_data.get("score", 5.0))
            result["max_score"] = int(grading_data.get("max_score", 10))
            result["grade_letter"] = grading_data.get("grade_letter", "C")
            result["passed"] = grading_data.get("passed", result["score"] >= 5.0)
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse grading output: {e}")

        # Parse feedback result
        try:
            feedback_data = _extract_json(str(feedback_task.output))
            result["mistakes"] = feedback_data.get("mistakes", [])
            result["strengths"] = feedback_data.get("strengths", [])
            result["feedback"] = feedback_data.get("feedback", "")
            result["recommendations"] = feedback_data.get("recommendations", [])
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse feedback output: {e}")

        # Parse review result
        try:
            review_data = _extract_json(str(review_task.output))
            result["encouragement"] = review_data.get("encouragement", "")
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse review output: {e}")

        return result

    def _combine_mcq_results(self, feedback_task, review_task, score, grade_letter, passed) -> dict:
        """Combine MCQ deterministic score with agent outputs."""
        result = {
            "score": score,
            "max_score": 10,
            "grade_letter": grade_letter,
            "passed": passed,
            "mistakes": [],
            "strengths": [],
            "feedback": "",
            "recommendations": [],
            "encouragement": "",
        }

        try:
            feedback_data = _extract_json(str(feedback_task.output))
            result["mistakes"] = feedback_data.get("mistakes", [])
            result["strengths"] = feedback_data.get("strengths", [])
            result["feedback"] = feedback_data.get("feedback", "")
            result["recommendations"] = feedback_data.get("recommendations", [])
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse MCQ feedback: {e}")

        try:
            review_data = _extract_json(str(review_task.output))
            result["encouragement"] = review_data.get("encouragement", "")
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse MCQ review: {e}")

        return result


    def generate_question(
        self,
        topic: str,
        difficulty: str,
        question_type: str = "written",
        category: str = "concept",
        previous_questions: list = None,
    ) -> dict:
        """
        Generate an interview-style question using a single-agent crew.
        Returns dict with question_text, correct_answer, explanation, options, code_snippet.
        """
        generator_llm = _build_llm(settings.GENERATOR_MODEL)

        generator = Agent(
            role=GENERATOR_ROLE,
            goal=GENERATOR_GOAL,
            backstory=GENERATOR_BACKSTORY,
            llm=generator_llm,
            verbose=self.verbose,
            allow_delegation=False,
        )

        prompt = get_prompt(
            category=category,
            question_type=question_type,
            topic=topic,
            difficulty=difficulty,
            previous_questions=previous_questions or [],
        )

        gen_task = Task(
            description=prompt,
            expected_output=GENERATOR_EXPECTED_OUTPUT,
            agent=generator,
        )

        crew = Crew(
            agents=[generator],
            tasks=[gen_task],
            process=Process.sequential,
            verbose=self.verbose,
        )

        crew.kickoff()

        # Parse the result
        try:
            data = _extract_json(str(gen_task.output))
            result = {
                "question_text": data.get("question_text", ""),
                "correct_answer": data.get("correct_answer", ""),
                "explanation": data.get("explanation", ""),
            }
            if question_type == "multiple_choice":
                result["options"] = data.get("options", {})
            if data.get("code_snippet"):
                result["code_snippet"] = data["code_snippet"]
            return result
        except Exception as e:
            logger.error(f"Failed to parse generated question: {e}")
            raise ValueError(f"Question generation failed: {e}")


grading_crew = GradingCrew()
