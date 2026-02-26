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
- Make the question UNIQUE and SPECIFIC — do not ask generic questions

Here is an example of the EXACT JSON format you must return:
{{"question_text": "Write a Python function called `is_palindrome(s)` that takes a string and returns True if it reads the same forwards and backwards (case-insensitive, ignoring spaces).", "correct_answer": "def is_palindrome(s):\\n    cleaned = s.lower().replace(' ', '')\\n    return cleaned == cleaned[::-1]", "explanation": "The function normalizes the string by lowering case and removing spaces, then compares it to its reverse."}}

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
- Make the question SPECIFIC to {topic} — avoid generic questions

Here is an example of the EXACT JSON format you must return:
{{"question_text": "Explain the difference between a stack and a queue. When would you use each one?", "correct_answer": "A stack follows Last-In-First-Out (LIFO) — the last element added is the first removed. A queue follows First-In-First-Out (FIFO) — the first element added is the first removed. Use a stack for undo operations, function call tracking, or DFS. Use a queue for task scheduling, BFS, or message processing.", "explanation": "This tests understanding of two fundamental data structures and their practical applications."}}

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

Here is an example of the EXACT JSON format you must return:
{{"question_text": "Find and fix the bug in this function that should return the sum of even numbers in a list:\\n\\ndef sum_evens(nums):\\n    total = 0\\n    for n in nums:\\n        if n % 2 == 1:\\n            total += n\\n    return total", "correct_answer": "The bug is in the condition: `n % 2 == 1` checks for odd numbers instead of even. Fix: change to `n % 2 == 0`.\\n\\ndef sum_evens(nums):\\n    total = 0\\n    for n in nums:\\n        if n % 2 == 0:\\n            total += n\\n    return total", "code_snippet": "def sum_evens(nums):\\n    total = 0\\n    for n in nums:\\n        if n % 2 == 1:\\n            total += n\\n    return total", "explanation": "The modulo check was inverted — checking for odd (remainder 1) instead of even (remainder 0)."}}

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

Here is an example of the EXACT JSON format you must return:
{{"question_text": "How would you design a URL shortener service like bit.ly?", "correct_answer": "Key components: 1) API server to accept long URLs and return short codes, 2) Database to store mappings (short_code -> long_url), 3) Base62 encoding of auto-increment ID for short codes, 4) 301 redirect on GET requests. For scale: add caching (Redis) for popular URLs, use a distributed ID generator, and add rate limiting.", "explanation": "This tests the ability to design a complete web service with storage, encoding, and scalability considerations."}}

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

Here is an example of the EXACT JSON format you must return:
{{"question_text": "Tell me about a time when you had to debug a critical production issue under pressure. What was your approach?", "correct_answer": "A strong answer uses the STAR format: Situation (describe the incident), Task (your role and responsibility), Action (systematic debugging: check logs, reproduce, isolate, fix, verify), Result (resolution, postmortem, preventive measures). Key points: staying calm, communicating with stakeholders, prioritizing correctly.", "explanation": "This reveals how candidates handle stress, their debugging methodology, and communication skills during incidents."}}

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

Here is an example of the EXACT JSON format you must return:
{{"question_text": "Review this Python function and identify all issues:\\n\\ndef get_user(id):\\n    data = open('users.json').read()\\n    users = eval(data)\\n    for u in users:\\n        if u['id'] == id:\\n            return u\\n    return None", "correct_answer": "Issues: 1) Using eval() is a security vulnerability — use json.loads() instead, 2) File is never closed — use a `with` statement, 3) Parameter name `id` shadows the built-in, 4) No error handling for missing file or invalid JSON, 5) Linear search is inefficient for large datasets.", "code_snippet": "def get_user(id):\\n    data = open('users.json').read()\\n    users = eval(data)\\n    for u in users:\\n        if u['id'] == id:\\n            return u\\n    return None", "explanation": "This code has security (eval), resource management (file handle), naming, and performance issues."}}

IMPORTANT: Do NOT repeat these previously asked questions:
{previous_questions}

Return ONLY the JSON object. No markdown. No code blocks. No extra text.""",
}

# MCQ variant — wraps any category into MCQ format
MCQ_WRAPPER = """Generate a {difficulty} difficulty MULTIPLE CHOICE question about {topic}.
Category: {category}

CRITICAL RULES:
- The question MUST be specifically about {topic}. Do NOT ask about unrelated topics.
- All 4 options must be plausible (no obviously wrong answers)
- Only one option should be the best/correct answer
- "correct_answer" MUST be ONLY the letter: "A", "B", "C", or "D"
- "options" MUST be a JSON object with keys "A", "B", "C", "D"
- DO NOT copy the example below — create a NEW question about {topic}

JSON format (DO NOT COPY THIS — create your own about {topic}):
{{"question_text": "<your question about {topic}>", "options": {{"A": "<option>", "B": "<option>", "C": "<option>", "D": "<option>"}}, "correct_answer": "<A or B or C or D>", "explanation": "<why correct answer is right>"}}

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
