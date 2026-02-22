import { useState } from "react";
import {
    FileText,
    PenLine,
    CircleDot,
    HelpCircle,
    CheckCircle2,
    GraduationCap,
    ClipboardList,
    RotateCcw,
    Send,
} from "lucide-react";
import "./GradeForm.css";

export default function GradeForm({ onSubmit, isLoading }) {
    const [questionType, setQuestionType] = useState("written");
    const [question, setQuestion] = useState("");
    const [correctAnswer, setCorrectAnswer] = useState("");
    const [studentAnswer, setStudentAnswer] = useState("");
    const [options, setOptions] = useState({ A: "", B: "", C: "", D: "" });
    const [correctOption, setCorrectOption] = useState("A");
    const [studentOption, setStudentOption] = useState("A");

    const handleSubmit = (e) => {
        e.preventDefault();

        const payload = {
            question_type: questionType,
            question,
        };

        if (questionType === "multiple_choice") {
            payload.options = options;
            payload.correct_answer = correctOption;
            payload.student_answer = studentOption;
        } else {
            payload.correct_answer = correctAnswer;
            payload.student_answer = studentAnswer;
        }

        onSubmit(payload);
    };

    const handleOptionChange = (key, value) => {
        setOptions((prev) => ({ ...prev, [key]: value }));
    };

    const handleReset = () => {
        setQuestion("");
        setCorrectAnswer("");
        setStudentAnswer("");
        setOptions({ A: "", B: "", C: "", D: "" });
        setCorrectOption("A");
        setStudentOption("A");
    };

    return (
        <form className="grade-form" onSubmit={handleSubmit}>
            <div className="form-header">
                <div className="form-icon"><FileText size={40} strokeWidth={1.5} /></div>
                <h2>Grade an Answer</h2>
                <p>Submit a question and answer for AI-powered grading</p>
            </div>

            {/* Question Type Toggle */}
            <div className="type-toggle">
                <button
                    type="button"
                    className={`toggle-btn ${questionType === "written" ? "active" : ""}`}
                    onClick={() => setQuestionType("written")}
                >
                    <PenLine size={18} />
                    Written
                </button>
                <button
                    type="button"
                    className={`toggle-btn ${questionType === "multiple_choice" ? "active" : ""}`}
                    onClick={() => setQuestionType("multiple_choice")}
                >
                    <CircleDot size={18} />
                    Multiple Choice
                </button>
            </div>

            {/* Question Field (always visible) */}
            <div className="form-group">
                <label htmlFor="question">
                    <HelpCircle size={16} />
                    Question
                </label>
                <textarea
                    id="question"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="Enter the exam question..."
                    rows={3}
                    required
                />
            </div>

            {questionType === "written" ? (
                <>
                    {/* Written: Correct Answer */}
                    <div className="form-group">
                        <label htmlFor="correct-answer">
                            <CheckCircle2 size={16} />
                            Correct Answer
                        </label>
                        <textarea
                            id="correct-answer"
                            value={correctAnswer}
                            onChange={(e) => setCorrectAnswer(e.target.value)}
                            placeholder="Enter the model/correct answer..."
                            rows={4}
                            required
                        />
                    </div>

                    {/* Written: Student Answer */}
                    <div className="form-group">
                        <label htmlFor="student-answer">
                            <GraduationCap size={16} />
                            Student Answer
                        </label>
                        <textarea
                            id="student-answer"
                            value={studentAnswer}
                            onChange={(e) => setStudentAnswer(e.target.value)}
                            placeholder="Enter the student's answer..."
                            rows={4}
                            required
                        />
                    </div>
                </>
            ) : (
                <>
                    {/* MCQ: Options */}
                    <div className="form-group options-group">
                        <label>
                            <ClipboardList size={16} />
                            Answer Options
                        </label>
                        <div className="options-grid">
                            {["A", "B", "C", "D"].map((key) => (
                                <div key={key} className="option-input">
                                    <span className="option-label">{key}</span>
                                    <input
                                        type="text"
                                        value={options[key]}
                                        onChange={(e) => handleOptionChange(key, e.target.value)}
                                        placeholder={`Option ${key}...`}
                                        required
                                    />
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* MCQ: Correct & Student Selection */}
                    <div className="mcq-selectors">
                        <div className="form-group selector-group">
                            <label htmlFor="correct-option">
                                <CheckCircle2 size={16} />
                                Correct Answer
                            </label>
                            <div className="option-buttons">
                                {["A", "B", "C", "D"].map((key) => (
                                    <button
                                        key={key}
                                        type="button"
                                        className={`option-btn correct ${correctOption === key ? "selected" : ""}`}
                                        onClick={() => setCorrectOption(key)}
                                    >
                                        {key}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div className="form-group selector-group">
                            <label htmlFor="student-option">
                                <GraduationCap size={16} />
                                Student Selected
                            </label>
                            <div className="option-buttons">
                                {["A", "B", "C", "D"].map((key) => (
                                    <button
                                        key={key}
                                        type="button"
                                        className={`option-btn student ${studentOption === key ? "selected" : ""}`}
                                        onClick={() => setStudentOption(key)}
                                    >
                                        {key}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                </>
            )}

            {/* Actions */}
            <div className="form-actions">
                <button
                    type="button"
                    className="btn-reset"
                    onClick={handleReset}
                    disabled={isLoading}
                >
                    <RotateCcw size={16} />
                    Clear
                </button>
                <button
                    type="submit"
                    className="btn-submit"
                    disabled={isLoading}
                >
                    {isLoading ? (
                        <>
                            <span className="spinner"></span>
                            Grading...
                        </>
                    ) : (
                        <>
                            <Send size={18} />
                            Grade Now
                        </>
                    )}
                </button>
            </div>
        </form>
    );
}
