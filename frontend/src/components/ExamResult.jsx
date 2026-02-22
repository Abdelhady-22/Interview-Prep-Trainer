import {
    CheckCircle2,
    XCircle,
    MessageSquare,
    BookOpen,
    ArrowRight,
    Sparkles,
} from "lucide-react";
import "./ExamResult.css";

export default function ExamResult({ result, currentIndex, totalQuestions, onNext }) {
    const isCorrect = result.is_correct;

    return (
        <div className={`result-card ${isCorrect ? "correct" : "incorrect"}`}>
            {/* Status Header */}
            <div className="result-header">
                <div className={`result-icon ${isCorrect ? "icon-correct" : "icon-incorrect"}`}>
                    {isCorrect ? <CheckCircle2 size={40} /> : <XCircle size={40} />}
                </div>
                <h2>{isCorrect ? "Correct!" : "Not Quite Right"}</h2>
                <div className="result-score-badge">
                    {result.score.toFixed(1)} / 10
                </div>
            </div>

            {/* Correct Answer */}
            {!isCorrect && (
                <div className="result-section correct-answer-section">
                    <h4>
                        <BookOpen size={16} />
                        Correct Answer
                    </h4>
                    <p>{result.correct_answer}</p>
                </div>
            )}

            {/* Feedback */}
            {result.feedback && (
                <div className="result-section">
                    <h4>
                        <MessageSquare size={16} />
                        Feedback
                    </h4>
                    <p>{result.feedback}</p>
                </div>
            )}

            {/* Encouragement */}
            {result.encouragement && (
                <div className="result-section encouragement-section">
                    <Sparkles size={16} />
                    <p>{result.encouragement}</p>
                </div>
            )}

            {/* Progress Info */}
            <div className="result-progress">
                <span>Score so far: {result.score_so_far?.toFixed(1) || 0} / {totalQuestions * 10}</span>
                <span>Questions remaining: {totalQuestions - (currentIndex - 1)}</span>
            </div>

            {/* Next Button */}
            <button className="next-btn" onClick={onNext}>
                <ArrowRight size={20} />
                Next Question
            </button>
        </div>
    );
}
