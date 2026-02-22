import { useState, useEffect } from "react";
import {
    BarChart3,
    Inbox,
    CircleDot,
    PenLine,
    CheckCircle,
    XCircle,
    ChevronUp,
    ChevronDown,
} from "lucide-react";
import { getSubmissions, getSubmissionById } from "../api/grader";
import "./SubmissionList.css";

export default function SubmissionList({ refreshKey }) {
    const [submissions, setSubmissions] = useState([]);
    const [expanded, setExpanded] = useState(null);
    const [detail, setDetail] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchSubmissions();
    }, [refreshKey]);

    const fetchSubmissions = async () => {
        try {
            const data = await getSubmissions();
            setSubmissions(data);
        } catch (err) {
            console.error("Failed to fetch submissions:", err);
        }
    };

    const toggleExpand = async (id) => {
        if (expanded === id) {
            setExpanded(null);
            setDetail(null);
            return;
        }

        setExpanded(id);
        setLoading(true);
        try {
            const data = await getSubmissionById(id);
            setDetail(data);
        } catch (err) {
            console.error("Failed to fetch detail:", err);
        } finally {
            setLoading(false);
        }
    };

    const getGradeColor = (letter) => {
        const colors = { A: "#10b981", B: "#3b82f6", C: "#f59e0b", D: "#f97316", F: "#ef4444" };
        return colors[letter] || "#94a3b8";
    };

    const formatDate = (dateStr) => {
        return new Date(dateStr).toLocaleDateString("en-US", {
            month: "short",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
        });
    };

    if (submissions.length === 0) {
        return (
            <div className="submissions-empty">
                <div className="empty-icon"><Inbox size={48} strokeWidth={1.5} /></div>
                <h3>No Submissions Yet</h3>
                <p>Grade your first answer to see it here</p>
            </div>
        );
    }

    return (
        <div className="submissions-container">
            <div className="submissions-header">
                <div className="sh-icon"><BarChart3 size={24} /></div>
                <h2>Submission History</h2>
                <span className="count-badge">{submissions.length}</span>
            </div>

            <div className="submissions-list">
                {submissions.map((sub) => (
                    <div
                        key={sub.id}
                        className={`submission-item ${expanded === sub.id ? "expanded" : ""}`}
                    >
                        <div
                            className="submission-summary"
                            onClick={() => toggleExpand(sub.id)}
                        >
                            <div className="sub-left">
                                <span className="sub-type-badge">
                                    {sub.question_type === "multiple_choice"
                                        ? <><CircleDot size={12} /> MCQ</>
                                        : <><PenLine size={12} /> Written</>
                                    }
                                </span>
                                <p className="sub-question">{sub.question}</p>
                            </div>

                            <div className="sub-right">
                                <span
                                    className="sub-grade"
                                    style={{ color: getGradeColor(sub.grade_letter) }}
                                >
                                    {sub.grade_letter}
                                </span>
                                <span className="sub-score">{sub.score}/{sub.max_score}</span>
                                <span className={`sub-pass ${sub.passed ? "pass" : "fail"}`}>
                                    {sub.passed ? <CheckCircle size={16} /> : <XCircle size={16} />}
                                </span>
                                <span className="sub-date">{formatDate(sub.created_at)}</span>
                                <span className="sub-chevron">
                                    {expanded === sub.id ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                                </span>
                            </div>
                        </div>

                        {expanded === sub.id && (
                            <div className="submission-detail">
                                {loading ? (
                                    <div className="detail-loading">Loading details...</div>
                                ) : detail ? (
                                    <>
                                        <div className="detail-section">
                                            <strong>Question:</strong>
                                            <p>{detail.question}</p>
                                        </div>
                                        <div className="detail-row">
                                            <div className="detail-section">
                                                <strong>Correct Answer:</strong>
                                                <p>{detail.correct_answer}</p>
                                            </div>
                                            <div className="detail-section">
                                                <strong>Student Answer:</strong>
                                                <p>{detail.student_answer}</p>
                                            </div>
                                        </div>
                                        {detail.options && (
                                            <div className="detail-section">
                                                <strong>Options:</strong>
                                                <div className="detail-options">
                                                    {Object.entries(detail.options).map(([k, v]) => (
                                                        <span
                                                            key={k}
                                                            className={`detail-opt ${k === detail.correct_answer ? "correct" : ""} ${k === detail.student_answer ? "selected" : ""}`}
                                                        >
                                                            {k}) {v}
                                                        </span>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                        {detail.feedback && (
                                            <div className="detail-section">
                                                <strong>Feedback:</strong>
                                                <p>{detail.feedback}</p>
                                            </div>
                                        )}
                                        {detail.mistakes && detail.mistakes.length > 0 && (
                                            <div className="detail-section">
                                                <strong>Mistakes:</strong>
                                                <ul>
                                                    {detail.mistakes.map((m, i) => (
                                                        <li key={i}>
                                                            <span className="tag">{m.type}</span> {m.description}
                                                        </li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}
                                        {detail.strengths && detail.strengths.length > 0 && (
                                            <div className="detail-section">
                                                <strong>Strengths:</strong>
                                                <ul>
                                                    {detail.strengths.map((s, i) => (
                                                        <li key={i}>{s}</li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}
                                    </>
                                ) : null}
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}
