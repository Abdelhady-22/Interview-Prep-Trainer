import { useState } from "react";
import { Send, Loader2, BarChart3, Code2 } from "lucide-react";
import { submitAnswer } from "../api/grader";
import Timer from "./Timer";
import HintButton from "./HintButton";
import "./QuestionCard.css";

export default function QuestionCard({
    examId,
    question,
    currentIndex,
    totalQuestions,
    scoreSoFar,
    onAnswerSubmitted,
    timeLimit = null,
    hintsAllowed = true,
    mode = "practice",
}) {
    const [answer, setAnswer] = useState("");
    const [selectedOption, setSelectedOption] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState(null);

    const isWritten = question.question_type !== "multiple_choice";
    const progress = ((currentIndex - 1) / totalQuestions) * 100;

    const handleSubmit = async () => {
        const studentAnswer = isWritten ? answer : selectedOption;
        if (!studentAnswer.trim()) return;

        setIsSubmitting(true);
        setError(null);

        try {
            const result = await submitAnswer({
                exam_id: examId,
                answer: studentAnswer,
            });
            setAnswer("");
            setSelectedOption("");
            onAnswerSubmitted(result);
        } catch (err) {
            setError(err.message);
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === "Enter" && e.ctrlKey && isWritten) {
            handleSubmit();
        }
    };

    const handleTimeUp = async () => {
        // Auto-submit current answer (or empty string) when timer runs out
        const studentAnswer = isWritten ? answer : selectedOption;
        setIsSubmitting(true);
        try {
            const result = await submitAnswer({
                exam_id: examId,
                answer: studentAnswer || "[Time expired — no answer submitted]",
            });
            setAnswer("");
            setSelectedOption("");
            onAnswerSubmitted(result);
        } catch (err) {
            setError(err.message);
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="question-card">
            {/* Progress Bar */}
            <div className="progress-section">
                <div className="progress-info">
                    <span className="progress-label">
                        Question {currentIndex} of {totalQuestions}
                    </span>
                    <span className="progress-score">
                        <BarChart3 size={14} />
                        Score: {scoreSoFar.toFixed(1)}
                    </span>
                </div>
                <div className="progress-bar">
                    <div className="progress-fill" style={{ width: `${progress}%` }}></div>
                </div>

                {/* Timer (for timed and mock modes) */}
                {timeLimit && (
                    <div className="timer-wrapper">
                        <Timer
                            seconds={timeLimit}
                            onTimeUp={handleTimeUp}
                            paused={isSubmitting}
                        />
                    </div>
                )}
            </div>

            {/* Question */}
            <div className="question-body">
                <div className="question-badges">
                    <span className="question-badge">
                        {question.topic?.replace("_", " ")} • {question.difficulty}
                    </span>
                    {question.category && (
                        <span className="question-badge category-badge">
                            {question.category.replace("_", " ")}
                        </span>
                    )}
                </div>
                <h3 className="question-text">{question.question_text}</h3>
                {question.code_snippet && (
                    <div className="code-snippet-block">
                        <div className="code-snippet-header">
                            <Code2 size={14} />
                            Code
                        </div>
                        <pre className="code-snippet-pre">
                            <code>{question.code_snippet}</code>
                        </pre>
                    </div>
                )}
            </div>

            {/* Hint Button (for practice and mock modes) */}
            {hintsAllowed && (
                <HintButton examId={examId} disabled={isSubmitting} />
            )}

            {/* Answer Input */}
            {isWritten ? (
                <div className="answer-section">
                    <label className="answer-label">Your Answer</label>
                    <textarea
                        className="answer-textarea"
                        value={answer}
                        onChange={(e) => setAnswer(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Type your answer here... (Ctrl+Enter to submit)"
                        rows={5}
                        disabled={isSubmitting}
                    />
                </div>
            ) : (
                <div className="answer-section">
                    <label className="answer-label">Select your answer</label>
                    <div className="options-list">
                        {question.options &&
                            Object.entries(question.options).map(([key, val]) => (
                                <button
                                    key={key}
                                    className={`option-card ${selectedOption === key ? "selected" : ""}`}
                                    onClick={() => setSelectedOption(key)}
                                    disabled={isSubmitting}
                                >
                                    <span className="option-key">{key}</span>
                                    <span className="option-text">{val}</span>
                                </button>
                            ))}
                    </div>
                </div>
            )}

            {error && <div className="question-error">{error}</div>}

            {/* Submit Button */}
            <button
                className="submit-answer-btn"
                onClick={handleSubmit}
                disabled={isSubmitting || (isWritten ? !answer.trim() : !selectedOption)}
            >
                {isSubmitting ? (
                    <>
                        <Loader2 size={18} className="spin" />
                        Grading...
                    </>
                ) : (
                    <>
                        <Send size={18} />
                        Submit Answer
                    </>
                )}
            </button>
        </div>
    );
}
