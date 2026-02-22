import {
    Trophy,
    CheckCircle2,
    XCircle,
    RotateCcw,
    Award,
} from "lucide-react";
import "./ExamSummary.css";

export default function ExamSummary({ summary, onNewExam }) {
    const percentage = summary.percentage || 0;
    const passed = summary.passed;

    return (
        <div className="summary-card">
            {/* Header */}
            <div className="summary-header">
                <div className={`trophy-icon ${passed ? "passed" : "failed"}`}>
                    {passed ? <Trophy size={48} /> : <Award size={48} />}
                </div>
                <h2>{passed ? "Exam Passed!" : "Exam Completed"}</h2>
                <p className="summary-subtitle">
                    {summary.topic?.replace("_", " ")} • {summary.difficulty}
                </p>
            </div>

            {/* Score Ring */}
            <div className="score-ring-container">
                <div className={`score-ring ${passed ? "ring-pass" : "ring-fail"}`}>
                    <span className="ring-percentage">{percentage.toFixed(0)}%</span>
                    <span className="ring-grade">{summary.grade_letter}</span>
                </div>
                <div className="score-detail">
                    <span>{summary.total_score?.toFixed(1)} / {summary.max_score}</span>
                    <span>Total Score</span>
                </div>
            </div>

            {/* Questions Review */}
            <div className="questions-review">
                <h3>Question Review</h3>
                {summary.questions?.map((q, idx) => (
                    <div key={idx} className={`review-item ${q.is_correct ? "item-correct" : "item-incorrect"}`}>
                        <div className="review-header">
                            <span className="review-num">
                                {q.is_correct ? (
                                    <CheckCircle2 size={18} />
                                ) : (
                                    <XCircle size={18} />
                                )}
                                Q{idx + 1}
                            </span>
                            <span className="review-score">{q.score?.toFixed(1)}/10</span>
                        </div>
                        <p className="review-question">{q.question_text}</p>
                        <div className="review-answers">
                            <div className="review-answer">
                                <span className="answer-tag your">Your Answer</span>
                                <span>{q.student_answer}</span>
                            </div>
                            {!q.is_correct && (
                                <div className="review-answer">
                                    <span className="answer-tag correct">Correct</span>
                                    <span>{q.correct_answer}</span>
                                </div>
                            )}
                        </div>
                        {q.feedback && <p className="review-feedback">{q.feedback}</p>}
                    </div>
                ))}
            </div>

            {/* New Exam Button */}
            <button className="new-exam-btn" onClick={onNewExam}>
                <RotateCcw size={20} />
                Take Another Exam
            </button>
        </div>
    );
}
