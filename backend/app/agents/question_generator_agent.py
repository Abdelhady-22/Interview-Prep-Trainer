"""
Interview Question Generator Agent — Generates interview-style programming questions.
Supports 6 categories: coding, concept, debug, system_design, behavioral, code_review.
All prompts enforce strict JSON-only output for structured parsing.
"""

GENERATOR_ROLE = "Senior Technical Interviewer"

GENERATOR_GOAL = (
    "Generate clear, realistic, interview-quality programming questions. "
    "Each question must closely mimic what a real interviewer would ask, "
    "have a definitive correct answer, and be suitable for automatic grading."
)

GENERATOR_BACKSTORY = (
    "You are a senior software engineer who has conducted hundreds of technical "
    "interviews at top tech companies. You know exactly what questions reveal "
    "a candidate's true understanding and problem-solving ability. You write "
    "clear, unambiguous questions with definitive correct answers."
)

# =============================================================================
# Category-specific prompt templates — each enforces strict JSON output
# =============================================================================

CATEGORY_PROMPTS = {
    # --- CODING: Write a function/algorithm ---
    "coding": """Generate a {difficulty} difficulty CODING interview question about {topic}.

The question should ask the candidate to write code (a function, algorithm, or short program).

Requirements:
- Ask to write a specific function or solve a specific problem with code
- The correct_answer must contain the complete working code solution
- For easy: simple logic (loops, conditions, basic operations)
- For medium: data manipulation, standard algorithms, string processing
- For hard: complex algorithms, optimization, advanced data structures

You must respond with ONLY this JSON object:
{{"question_text": "<describe what function to write, include expected input/output examples>", "correct_answer": "<complete working code solution>", "explanation": "<brief explanation of the approach, 1-2 sentences>"}}

IMPORTANT: Do NOT repeat these previously asked questions:
{previous_questions}

Return ONLY the JSON object. No markdown. No code blocks. No extra text.""",

    # --- CONCEPT: Explain a CS concept ---
    "concept": """Generate a {difficulty} difficulty CONCEPT interview question about {topic}.

The question should ask the candidate to explain a concept, compare ideas, or describe how something works.

Requirements:
- Ask "What is...", "Explain...", "Compare...", "Describe how..." type questions
- The correct_answer must be a clear, complete explanation
- For easy: basic definitions, fundamental concepts
- For medium: comparing concepts, explaining tradeoffs, how things work internally
- For hard: deep technical knowledge, edge cases, advanced theory

You must respond with ONLY this JSON object:
{{"question_text": "<the concept question>", "correct_answer": "<complete correct explanation>", "explanation": "<why this is the correct/complete answer, 1-2 sentences>"}}

IMPORTANT: Do NOT repeat these previously asked questions:
{previous_questions}

Return ONLY the JSON object. No markdown. No code blocks. No extra text.""",

    # --- DEBUG: Find and fix a bug ---
    "debug": """Generate a {difficulty} difficulty DEBUG interview question about {topic}.

The question should present buggy code and ask the candidate to identify and fix the bug.

Requirements:
- Include a code snippet with a realistic, non-obvious bug
- The question_text MUST contain the buggy code
- The correct_answer must identify the bug AND provide the fixed code
- For easy: syntax errors, off-by-one, wrong operator
- For medium: logic errors, edge case bugs, incorrect algorithm
- For hard: subtle bugs, race conditions, memory issues, complex logic errors

You must respond with ONLY this JSON object:
{{"question_text": "<describe the task, then show the buggy code and ask what is wrong and how to fix it>", "correct_answer": "<identify the bug and provide the corrected code>", "code_snippet": "<the buggy code by itself for display>", "explanation": "<what the bug was and why the fix works, 1-2 sentences>"}}

IMPORTANT: Do NOT repeat these previously asked questions:
{previous_questions}

Return ONLY the JSON object. No markdown. No code blocks. No extra text.""",

    # --- SYSTEM_DESIGN: Design a system ---
    "system_design": """Generate a {difficulty} difficulty SYSTEM DESIGN interview question about {topic}.

The question should ask the candidate to design or architect a system, component, or solution.

Requirements:
- Ask "How would you design...", "Architect a...", "Design a system that..." type questions
- The correct_answer must cover key components, data flow, and design decisions
- For easy: design a simple feature, basic class structure
- For medium: design a small system, API design, database schema
- For hard: large-scale system design, distributed systems, scalability

You must respond with ONLY this JSON object:
{{"question_text": "<the system design question>", "correct_answer": "<key components, data flow, and design decisions>", "explanation": "<what makes this a good design, 1-2 sentences>"}}

IMPORTANT: Do NOT repeat these previously asked questions:
{previous_questions}

Return ONLY the JSON object. No markdown. No code blocks. No extra text.""",

    # --- BEHAVIORAL: Technical behavioral (STAR format) ---
    "behavioral": """Generate a {difficulty} difficulty BEHAVIORAL interview question related to {topic}.

The question should be a technical behavioral question that asks about past experience or how the candidate would handle a situation.

Requirements:
- Ask "Tell me about a time when...", "How would you handle...", "Describe a situation where..." type questions
- The correct_answer must describe what a strong answer looks like (key points to cover)
- The question should relate to {topic} but focus on soft skills, teamwork, problem-solving
- For easy: basic teamwork, code review, helping others
- For medium: conflict resolution, technical disagreements, deadline pressure
- For hard: leading a failing project, making difficult technical decisions, handling production incidents

You must respond with ONLY this JSON object:
{{"question_text": "<the behavioral question>", "correct_answer": "<what a strong answer should include: key points, STAR format expectations>", "explanation": "<what interviewers look for in this answer, 1-2 sentences>"}}

IMPORTANT: Do NOT repeat these previously asked questions:
{previous_questions}

Return ONLY the JSON object. No markdown. No code blocks. No extra text.""",

    # --- CODE_REVIEW: Review given code ---
    "code_review": """Generate a {difficulty} difficulty CODE REVIEW interview question about {topic}.

The question should present code and ask the candidate to review it — identify issues, suggest improvements, or evaluate quality.

Requirements:
- Include a code snippet that has specific reviewable issues
- The question_text MUST contain the code to review
- The correct_answer must list the issues and improvements
- For easy: naming, formatting, missing error handling
- For medium: performance issues, code smells, SOLID violations
- For hard: architectural issues, security vulnerabilities, subtle antipatterns

You must respond with ONLY this JSON object:
{{"question_text": "<present the code and ask the candidate to review it>", "correct_answer": "<list of issues found and suggested improvements>", "code_snippet": "<the code to review by itself for display>", "explanation": "<summary of the key issues, 1-2 sentences>"}}

IMPORTANT: Do NOT repeat these previously asked questions:
{previous_questions}

Return ONLY the JSON object. No markdown. No code blocks. No extra text.""",
}

# MCQ variant — wraps any category into MCQ format
MCQ_WRAPPER = """Generate a {difficulty} difficulty MULTIPLE CHOICE question about {topic}.
Category: {category}

The question should test the candidate's knowledge in an interview setting.

Requirements:
- All 4 options should be plausible (no obviously wrong answers)
- Only one option should be the best/correct answer
- For easy: basic knowledge
- For medium: applied understanding
- For hard: deep expertise, edge cases

You must respond with ONLY this JSON object:
{{"question_text": "<the interview question>", "options": {{"A": "<option A>", "B": "<option B>", "C": "<option C>", "D": "<option D>"}}, "correct_answer": "<A, B, C, or D>", "explanation": "<why the correct answer is right, 1-2 sentences>"}}

IMPORTANT: Do NOT repeat these previously asked questions:
{previous_questions}

Return ONLY the JSON object. No markdown. No code blocks. No extra text."""


def get_prompt(category: str, question_type: str, topic: str, difficulty: str, previous_questions: list) -> str:
    """Get the appropriate prompt for the given category and question type."""
    prev_text = "None" if not previous_questions else "\n".join(f"- {q}" for q in previous_questions)

    if question_type == "multiple_choice":
        return MCQ_WRAPPER.format(
            topic=topic,
            difficulty=difficulty,
            category=category.replace("_", " "),
            previous_questions=prev_text,
        )

    template = CATEGORY_PROMPTS.get(category, CATEGORY_PROMPTS["concept"])
    return template.format(
        topic=topic,
        difficulty=difficulty,
        previous_questions=prev_text,
    )


GENERATOR_EXPECTED_OUTPUT = (
    "A valid JSON object with question_text, correct_answer, and explanation fields."
)
