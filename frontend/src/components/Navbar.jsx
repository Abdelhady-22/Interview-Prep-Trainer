import { Code2, History, Zap } from "lucide-react";
import "./Navbar.css";

export default function Navbar({ currentPage, onNavigate }) {
    const tabs = [
        { id: "exam", label: "Take Exam", icon: <Zap size={18} /> },
        { id: "history", label: "Exam History", icon: <History size={18} /> },
    ];

    return (
        <nav className="navbar">
            <div className="nav-brand">
                <Code2 size={28} />
                <span>Interview Prep Trainer</span>
            </div>
            <div className="nav-tabs">
                {tabs.map((tab) => (
                    <button
                        key={tab.id}
                        className={`nav-tab ${currentPage === tab.id ? "active" : ""}`}
                        onClick={() => onNavigate(tab.id)}
                    >
                        {tab.icon}
                        {tab.label}
                    </button>
                ))}
            </div>
        </nav>
    );
}
