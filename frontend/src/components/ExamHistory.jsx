import { useState, useEffect } from "react";
import { History, Clock, Trophy, ChevronRight, RefreshCw } from "lucide-react";
import { getExams } from "../api/grader";
import "./ExamHistory.css";

export default function ExamHistory() {
    const [exams, setExams] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        loadExams();
    }, []);

    const loadExams = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await getExams();
            setExams(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const formatDate = (isoStr) => {
        if (!isoStr) return "";
        const d = new Date(isoStr);
        return d.toLocaleDateString("en-US", {
            month: "short",
            day: "numeric",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit",
        });
    };

    const getDifficultyClass = (d) => {
        if (d === "easy") return "diff-easy";
        if (d === "medium") return "diff-medium";
        return "diff-hard";
    };

    return (
        <div className="history-page">
            <div className="history-header">
                <div>
                    <h2>
                        <History size={24} />
                        Exam History
                    </h2>
                    <p>Your past exam sessions and results</p>
                </div>
                <button className="refresh-btn" onClick={loadExams}>
                    <RefreshCw size={16} />
                </button>
            </div>

            {loading && (
                <div className="history-loading">Loading exams...</div>
            )}

            {error && (
                <div className="history-error">{error}</div>
            )}

            {!loading && !error && exams.length === 0 && (
                <div className="history-empty">
                    <Trophy size={48} strokeWidth={1.5} />
                    <h3>No exams yet</h3>
                    <p>Take your first programming exam to see your results here</p>
                </div>
            )}

            {!loading && exams.length > 0 && (
                <div className="history-list">
                    {exams.map((exam) => (
                        <div key={exam.exam_id} className="history-item">
                            <div className="item-left">
                                <div className="item-topic">
                                    {exam.topic?.replace("_", " ")}
                                </div>
                                <div className="item-meta">
                                    <span className={`item-diff ${getDifficultyClass(exam.difficulty)}`}>
                                        {exam.difficulty}
                                    </span>
                                    <span className="item-type">{exam.question_type?.replace("_", " ")}</span>
                                    {exam.category && (
                                        <span className="item-category">{exam.category.replace("_", " ")}</span>
                                    )}
                                    {exam.mode && exam.mode !== "practice" && (
                                        <span className="item-mode">{exam.mode}</span>
                                    )}
                                    <span className="item-questions">{exam.total_questions}Q</span>
                                </div>
                                <div className="item-date">
                                    <Clock size={12} />
                                    {formatDate(exam.created_at)}
                                </div>
                            </div>
                            <div className="item-right">
                                <div className={`item-grade ${exam.percentage >= 50 ? "grade-pass" : "grade-fail"}`}>
                                    {exam.grade_letter}
                                </div>
                                <div className="item-percentage">{exam.percentage?.toFixed(0)}%</div>
                                <div className="item-status">{exam.status}</div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
