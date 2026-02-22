import { useState, useEffect } from "react";
import {
    Play,
    BookOpen,
    Gauge,
    Hash,
    Sparkles,
    Loader2,
    PenLine,
    CircleDot,
    Layers,
    Zap,
} from "lucide-react";
import { startExam, getTopics } from "../api/grader";
import QuestionCard from "./QuestionCard";
import ExamResult from "./ExamResult";
import ExamSummary from "./ExamSummary";
import "./ExamPage.css";

export default function ExamPage() {
    // States: setup | loading | question | result | summary
    const [phase, setPhase] = useState("setup");
    const [topics, setTopics] = useState([]);
    const [selectedTopic, setSelectedTopic] = useState("");
    const [selectedDifficulty, setSelectedDifficulty] = useState("easy");
    const [selectedType, setSelectedType] = useState("written");
    const [categories, setCategories] = useState([]);
    const [selectedCategory, setSelectedCategory] = useState("concept");
    const [modes, setModes] = useState([]);
    const [selectedMode, setSelectedMode] = useState("practice");
    const [timeLimit, setTimeLimit] = useState(null);
    const [hintsAllowed, setHintsAllowed] = useState(true);
    const [numQuestions, setNumQuestions] = useState(5);
    const [examId, setExamId] = useState(null);
    const [currentQuestion, setCurrentQuestion] = useState(null);
    const [currentIndex, setCurrentIndex] = useState(1);
    const [totalQuestions, setTotalQuestions] = useState(5);
    const [lastResult, setLastResult] = useState(null);
    const [examSummary, setExamSummary] = useState(null);
    const [error, setError] = useState(null);
    const [scoreSoFar, setScoreSoFar] = useState(0);
    // Store the correct_answer for the current question (for submission)
    const [currentCorrectAnswer, setCurrentCorrectAnswer] = useState("");

    useEffect(() => {
        loadTopics();
    }, []);

    const loadTopics = async () => {
        try {
            const data = await getTopics();
            setTopics(data.topics || []);
            if (data.topics?.length > 0) {
                setSelectedTopic(data.topics[0].id);
            }
            if (data.categories?.length > 0) {
                setCategories(data.categories);
                setSelectedCategory(data.categories[0].id);
            }
            if (data.modes?.length > 0) {
                setModes(data.modes);
            }
        } catch {
            // Fallback topics
            setTopics([
                { id: "python", name: "Python", icon: "🐍" },
                { id: "oop", name: "OOP", icon: "🏗️" },
                { id: "data_structures", name: "Data Structures", icon: "📊" },
                { id: "algorithms", name: "Algorithms", icon: "⚙️" },
                { id: "sql", name: "SQL", icon: "🗄️" },
                { id: "javascript", name: "JavaScript", icon: "🌐" },
            ]);
            setSelectedTopic("python");
        }
    };

    const handleStartExam = async () => {
        setPhase("loading");
        setError(null);
        try {
            const result = await startExam({
                topic: selectedTopic,
                difficulty: selectedDifficulty,
                num_questions: numQuestions,
                question_type: selectedType,
                category: selectedCategory,
                mode: selectedMode,
            });
            setExamId(result.exam_id);
            setCurrentQuestion(result.question);
            setTotalQuestions(result.total_questions);
            setCurrentIndex(result.current_index);
            setTimeLimit(result.time_limit_seconds || null);
            setScoreSoFar(0);
            // Store the correct answer (it comes hidden from the backend, but we need it)
            // Actually, the backend sanitizes it out. We'll store full question data separately.
            // The correct_answer will be sent back from the server when we answer.
            setPhase("question");
        } catch (err) {
            setError(err.message);
            setPhase("setup");
        }
    };

    const handleAnswerSubmitted = (result) => {
        setLastResult(result);
        setScoreSoFar(result.score_so_far || 0);

        if (result.exam_completed) {
            setExamSummary(result.exam_summary);
            setPhase("summary");
        } else {
            setPhase("result");
        }
    };

    const handleNextQuestion = () => {
        if (lastResult?.next_question) {
            setCurrentQuestion(lastResult.next_question);
            setCurrentIndex(lastResult.current_index);
            setPhase("question");
        }
    };

    const handleNewExam = () => {
        setPhase("setup");
        setExamId(null);
        setCurrentQuestion(null);
        setLastResult(null);
        setExamSummary(null);
        setScoreSoFar(0);
        setCurrentIndex(1);
    };

    return (
        <div className="exam-page">
            {/* Setup Phase */}
            {phase === "setup" && (
                <div className="setup-card">
                    <div className="setup-header">
                        <Sparkles size={40} strokeWidth={1.5} />
                        <h2>Start a Programming Exam</h2>
                        <p>Choose your topic and difficulty — the AI will generate questions for you</p>
                    </div>

                    {error && <div className="exam-error">{error}</div>}

                    {/* Topic Selection */}
                    <div className="setup-section">
                        <label className="setup-label">
                            <BookOpen size={16} />
                            Topic
                        </label>
                        <div className="topic-grid">
                            {topics.map((topic) => (
                                <button
                                    key={topic.id}
                                    className={`topic-btn ${selectedTopic === topic.id ? "selected" : ""}`}
                                    onClick={() => setSelectedTopic(topic.id)}
                                >
                                    <span className="topic-icon">{topic.icon}</span>
                                    <span className="topic-name">{topic.name}</span>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Category Selection */}
                    <div className="setup-section">
                        <label className="setup-label">
                            <Layers size={16} />
                            Interview Category
                        </label>
                        <div className="category-grid">
                            {categories.map((cat) => (
                                <button
                                    key={cat.id}
                                    className={`category-btn ${selectedCategory === cat.id ? "selected" : ""}`}
                                    onClick={() => setSelectedCategory(cat.id)}
                                >
                                    <span className="category-icon">{cat.icon}</span>
                                    <span className="category-info">
                                        <span className="category-name">{cat.name}</span>
                                        <span className="category-desc">{cat.description}</span>
                                    </span>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Mode Selection */}
                    {modes.length > 0 && (
                        <div className="setup-section">
                            <label className="setup-label">
                                <Zap size={16} />
                                Exam Mode
                            </label>
                            <div className="category-grid">
                                {modes.map((m) => (
                                    <button
                                        key={m.id}
                                        className={`category-btn ${selectedMode === m.id ? "selected" : ""}`}
                                        onClick={() => {
                                            setSelectedMode(m.id);
                                            setHintsAllowed(m.has_hints);
                                        }}
                                    >
                                        <span className="category-icon">{m.icon}</span>
                                        <span className="category-info">
                                            <span className="category-name">{m.name}</span>
                                            <span className="category-desc">{m.description}</span>
                                        </span>
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Difficulty Selection */}
                    <div className="setup-section">
                        <label className="setup-label">
                            <Gauge size={16} />
                            Difficulty
                        </label>
                        <div className="difficulty-row">
                            {["easy", "medium", "hard"].map((d) => (
                                <button
                                    key={d}
                                    className={`diff-btn diff-${d} ${selectedDifficulty === d ? "selected" : ""}`}
                                    onClick={() => setSelectedDifficulty(d)}
                                >
                                    {d.charAt(0).toUpperCase() + d.slice(1)}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Question Type */}
                    <div className="setup-section">
                        <label className="setup-label">
                            <PenLine size={16} />
                            Question Type
                        </label>
                        <div className="difficulty-row">
                            <button
                                className={`diff-btn ${selectedType === "written" ? "selected" : ""}`}
                                onClick={() => setSelectedType("written")}
                            >
                                <PenLine size={14} /> Written
                            </button>
                            <button
                                className={`diff-btn ${selectedType === "multiple_choice" ? "selected" : ""}`}
                                onClick={() => setSelectedType("multiple_choice")}
                            >
                                <CircleDot size={14} /> Multiple Choice
                            </button>
                        </div>
                    </div>

                    {/* Number of Questions */}
                    <div className="setup-section">
                        <label className="setup-label">
                            <Hash size={16} />
                            Number of Questions
                        </label>
                        <div className="num-row">
                            {[3, 5, 10].map((n) => (
                                <button
                                    key={n}
                                    className={`num-btn ${numQuestions === n ? "selected" : ""}`}
                                    onClick={() => setNumQuestions(n)}
                                >
                                    {n}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Start Button */}
                    <button className="start-btn" onClick={handleStartExam}>
                        <Play size={20} />
                        Start Exam
                    </button>
                </div>
            )}

            {/* Loading Phase */}
            {phase === "loading" && (
                <div className="loading-card">
                    <div className="loading-spinner">
                        <Loader2 size={48} className="spin" />
                    </div>
                    <h3>Generating your exam...</h3>
                    <p>The AI is crafting a {selectedDifficulty} {selectedCategory.replace("_", " ")} question about {selectedTopic.replace("_", " ")}</p>
                </div>
            )}

            {/* Question Phase */}
            {phase === "question" && currentQuestion && (
                <QuestionCard
                    examId={examId}
                    question={currentQuestion}
                    currentIndex={currentIndex}
                    totalQuestions={totalQuestions}
                    scoreSoFar={scoreSoFar}
                    onAnswerSubmitted={handleAnswerSubmitted}
                    timeLimit={timeLimit}
                    hintsAllowed={hintsAllowed}
                    mode={selectedMode}
                />
            )}

            {/* Result Phase (per-question) */}
            {phase === "result" && lastResult && (
                <ExamResult
                    result={lastResult}
                    currentIndex={currentIndex}
                    totalQuestions={totalQuestions}
                    onNext={handleNextQuestion}
                />
            )}

            {/* Summary Phase (exam complete) */}
            {phase === "summary" && examSummary && (
                <ExamSummary
                    summary={examSummary}
                    onNewExam={handleNewExam}
                />
            )}
        </div>
    );
}
