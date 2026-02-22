const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Start a new exam session.
 * @param {Object} data - { topic, difficulty, num_questions, question_type }
 * @returns {Promise<Object>} { exam_id, total_questions, current_index, question }
 */
export async function startExam(data) {
    const response = await fetch(`${API_URL}/exam/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "Failed to start exam" }));
        throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
}

/**
 * Submit an answer to the current question.
 * @param {Object} data - { exam_id, answer }
 * @returns {Promise<Object>} { is_correct, score, feedback, correct_answer, exam_completed, next_question? }
 */
export async function submitAnswer(data) {
    const response = await fetch(`${API_URL}/exam/answer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "Failed to submit answer" }));
        throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
}

/**
 * Get full exam state by ID.
 * @param {string} examId
 * @returns {Promise<Object>}
 */
export async function getExam(examId) {
    const response = await fetch(`${API_URL}/exam/${examId}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
}

/**
 * List all exam sessions (history).
 * @returns {Promise<Array>}
 */
export async function getExams() {
    const response = await fetch(`${API_URL}/exams`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
}

/**
 * Get available topics, difficulties, and question types.
 * @returns {Promise<Object>} { topics, difficulties, question_types }
 */
export async function getTopics() {
    const response = await fetch(`${API_URL}/topics`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
}

/**
 * Request a hint for the current question.
 * @param {string} examId
 * @returns {Promise<Object>} { hint, hints_used, score_penalty }
 */
export async function requestHint(examId) {
    const response = await fetch(`${API_URL}/exam/hint`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ exam_id: examId }),
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "Failed to get hint" }));
        throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
}

/**
 * Check backend health status.
 * @returns {Promise<Object>}
 */
export async function checkHealth() {
    const response = await fetch(`${API_URL}/health`);
    return response.json();
}
