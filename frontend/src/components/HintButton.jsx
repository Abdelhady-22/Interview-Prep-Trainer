import { useState } from "react";
import { Lightbulb, Loader2, AlertCircle } from "lucide-react";
import { requestHint } from "../api/grader";
import "./HintButton.css";

export default function HintButton({ examId, disabled = false }) {
    const [hints, setHints] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [penalty, setPenalty] = useState(0);

    const maxHints = 3;
    const hintsRemaining = maxHints - hints.length;

    const handleRequestHint = async () => {
        if (hints.length >= maxHints || loading) return;
        setLoading(true);
        setError(null);
        try {
            const result = await requestHint(examId);
            setHints((prev) => [...prev, result.hint]);
            setPenalty(result.score_penalty);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="hint-section">
            <button
                className="hint-btn"
                onClick={handleRequestHint}
                disabled={disabled || loading || hints.length >= maxHints}
            >
                {loading ? (
                    <>
                        <Loader2 size={16} className="spin" />
                        Generating hint...
                    </>
                ) : (
                    <>
                        <Lightbulb size={16} />
                        {hints.length >= maxHints
                            ? "No hints remaining"
                            : `Get Hint (${hintsRemaining} left)`}
                    </>
                )}
            </button>

            {penalty > 0 && (
                <div className="hint-penalty">
                    <AlertCircle size={12} />
                    Score penalty: -{Math.round(penalty * 100)}% of max
                </div>
            )}

            {error && <div className="hint-error">{error}</div>}

            {hints.length > 0 && (
                <div className="hint-list">
                    {hints.map((hint, i) => (
                        <div key={i} className="hint-card">
                            <div className="hint-header">
                                <Lightbulb size={14} />
                                Hint {i + 1}
                            </div>
                            <p className="hint-text">{hint}</p>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
