import { useState } from "react";
import Navbar from "./components/Navbar";
import ExamPage from "./components/ExamPage";
import ExamHistory from "./components/ExamHistory";
import "./App.css";

function App() {
    const [page, setPage] = useState("exam");

    return (
        <div className="app">
            {/* Background Effects */}
            <div className="bg-gradient"></div>
            <div className="bg-grid"></div>

            {/* Navigation */}
            <Navbar currentPage={page} onNavigate={setPage} />

            {/* Main Content */}
            <main className="app-main">
                {page === "exam" && <ExamPage />}
                {page === "history" && <ExamHistory />}
            </main>

            {/* Footer */}
            <footer className="app-footer">
                <p>Interview Prep Trainer — Built with FastAPI, CrewAI, React &amp; Ollama</p>
            </footer>
        </div>
    );
}

export default App;
