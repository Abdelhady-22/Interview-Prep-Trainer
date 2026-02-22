import {
    Trophy,
    BookOpen,
    CheckCircle,
    XCircle,
    MessageSquare,
    FileText,
    AlertTriangle,
    Zap,
    BookMarked,
} from "lucide-react";
import "./ResultCard.css";

export default function ResultCard({ result }) {
    if (!result) return null;

    const scorePercent = (result.score / result.max_score) * 100;
    const isPassed = result.passed;

    return (
        <div className={`result-card ${isPassed ? "passed" : "failed"}`}>
            <div className="result-header">
                <div className="result-icon">
                    {isPassed ? <Trophy size={40} strokeWidth={1.5} /> : <BookOpen size={40} strokeWidth={1.5} />}
                </div>
                <h2>Grading Result</h2>
            </div>

            {/* Score Section */}
            <div className="score-section">
                <div className="score-circle">
                    <svg viewBox="0 0 120 120" className="score-ring">
                        <circle cx="60" cy="60" r="50" className="ring-bg" />
                        <circle
                            cx="60"
                            cy="60"
                            r="50"
                            className="ring-fill"
                            style={{
                                strokeDasharray: `${scorePercent * 3.14} ${314 - scorePercent * 3.14}`,
                            }}
                        />
                    </svg>
                    <div className="score-text">
                        <span className="score-value">{result.score}</span>
                        <span className="score-max">/ {result.max_score}</span>
                    </div>
                </div>

                <div className="score-details">
                    <div className={`grade-badge grade-${result.grade_letter}`}>
                        {result.grade_letter}
                    </div>
                    <div className={`pass-badge ${isPassed ? "pass" : "fail"}`}>
                        {isPassed
                            ? <><CheckCircle size={14} /> PASSED</>
                            : <><XCircle size={14} /> FAILED</>
                        }
                    </div>
                </div>
            </div>

            {/* Encouragement */}
            {result.encouragement && (
                <div className="encouragement-box">
                    <MessageSquare size={20} className="enc-icon" />
                    <p>{result.encouragement}</p>
                </div>
            )}

            {/* Feedback */}
            {result.feedback && (
                <div className="section">
                    <h3><FileText size={16} /> Feedback</h3>
                    <p className="feedback-text">{result.feedback}</p>
                </div>
            )}

            {/* Mistakes */}
            {result.mistakes && result.mistakes.length > 0 && (
                <div className="section">
                    <h3><AlertTriangle size={16} /> Mistakes</h3>
                    <ul className="mistakes-list">
                        {result.mistakes.map((m, i) => (
                            <li key={i}>
                                <span className="mistake-type">{m.type}</span>
                                <span className="mistake-desc">{m.description}</span>
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Strengths */}
            {result.strengths && result.strengths.length > 0 && (
                <div className="section">
                    <h3><Zap size={16} /> Strengths</h3>
                    <ul className="strengths-list">
                        {result.strengths.map((s, i) => (
                            <li key={i}>{s}</li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Recommendations */}
            {result.recommendations && result.recommendations.length > 0 && (
                <div className="section">
                    <h3><BookMarked size={16} /> Recommendations</h3>
                    <div className="recommendations-grid">
                        {result.recommendations.map((r, i) => (
                            <div key={i} className="rec-card">
                                <div className="rec-topic">{r.topic}</div>
                                <div className="rec-action">{r.action}</div>
                                <span className="rec-type">{r.resource_type}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
