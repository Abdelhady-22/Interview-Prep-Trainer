# 🎯 Interview Prep Trainer

> AI-powered **technical interview preparation platform** — practice coding, system design, behavioral, and debug questions with **AI-generated questions, grading, hints, and timed modes**. Built with **FastAPI**, **CrewAI**, **React**, **PostgreSQL**, and **Ollama**.

---

## ✨ Features

### Core
- **AI-Generated Questions** — questions created on-the-fly by an LLM, never repeated
- **Automated Grading** — CrewAI multi-agent pipeline (or single-prompt mode) for scoring + feedback
- **Server-Side Answers** — correct answers never exposed to the frontend (anti-cheat)
- **Exam History** — track past sessions with grades, scores, and detailed review

### Interview Categories
| Category | Description |
|----------|-------------|
| 💻 **Coding** | Write functions and algorithms |
| 📖 **Concept** | Explain technical CS concepts |
| 🐛 **Debug** | Find and fix bugs in given code |
| 🏛️ **System Design** | Design systems and architectures |
| 🤝 **Behavioral** | Situational and teamwork questions (STAR format) |
| 🔍 **Code Review** | Identify issues and improvements in code |

### Exam Modes
| Mode | Timer | Hints | Purpose |
|------|-------|-------|---------|
| 📝 **Practice** | ❌ | ✅ 3/question | Learn at your own pace |
| ⏱️ **Timed Exam** | ✅ 5 min/q | ❌ | Simulate interview pressure |
| 🎤 **Mock Interview** | ✅ 7 min/q | ✅ 3/question | Closest to a real interview |

### Hints & Timer
- **Progressive Hints** — 3 levels per question (general → specific → near-answer), each costing 15% of max score
- **Countdown Timer** — visual urgency states (normal → yellow at 30s → red pulse at 10s), auto-submits on expiry
- **8 Topics** — Python, OOP, Data Structures, Algorithms, SQL, JavaScript, Java, Web Dev
- **3 Difficulty Levels** — Easy, Medium, Hard
- **2 Question Types** — Written (free-text) and Multiple Choice (A/B/C/D)

---

## 🏗️ Architecture

```
Browser → React (Vite) :3000
              ↓ HTTP
         FastAPI :8000
         ├── API Layer (routes, schemas)
         ├── Service Layer (exam, question, grading, hint, health)
         ├── Agent Layer (CrewAI: question generator + grading agents)
         ├── Repository Layer (SQLAlchemy CRUD)
         └── Integration Layer (Ollama HTTP client)
              ├── PostgreSQL :5432 (questions, exams tables)
              └── Ollama :11434 (LLM inference)
```

---

## 📁 Project Structure

```
Interview Prep Trainer/
├── docker-compose.yml          # 4-container orchestration
├── .env.example                # Environment template
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py             # FastAPI entry + CORS
│       ├── config.py           # Settings from env
│       ├── database.py         # SQLAlchemy engine
│       ├── api/
│       │   ├── routes.py       # /exam/start, /exam/answer, /exam/hint, /exams, /topics
│       │   └── schemas.py      # Pydantic models (CategoryEnum, ModeEnum, HintRequest, etc.)
│       ├── services/
│       │   ├── exam_service.py     # Full exam flow orchestration
│       │   ├── question_service.py # LLM question generation
│       │   ├── grading_service.py  # Answer grading (crew/single)
│       │   ├── hint_service.py     # Progressive hint generation
│       │   └── health_service.py   # Health checks
│       ├── agents/
│       │   ├── crew.py                     # CrewAI orchestration
│       │   ├── question_generator_agent.py # 6 category-specific prompt templates
│       │   ├── grader_agent.py             # Scoring agent
│       │   ├── feedback_agent.py           # Feedback agent
│       │   └── review_agent.py             # Encouragement agent
│       ├── repositories/
│       │   ├── exam_repository.py
│       │   ├── question_repository.py
│       │   └── submission_repository.py
│       ├── integrations/
│       │   └── ollama_client.py
│       └── models/
│           ├── exam.py          # mode, time_limit_seconds, hints_used, category
│           ├── question.py      # category column
│           └── submission.py
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   └── src/
│       ├── App.jsx                 # Navbar + page routing
│       ├── api/grader.js           # API client (startExam, submitAnswer, requestHint, etc.)
│       └── components/
│           ├── Navbar.jsx          # Navigation bar
│           ├── ExamPage.jsx        # Setup (topic, category, mode) → question → result → summary
│           ├── QuestionCard.jsx    # Question + answer input + Timer + HintButton
│           ├── Timer.jsx           # Countdown timer with urgency states
│           ├── HintButton.jsx      # Progressive hint UI (up to 3 hints)
│           ├── ExamResult.jsx      # Per-question feedback
│           ├── ExamSummary.jsx     # Final exam results
│           └── ExamHistory.jsx     # Past exam sessions
│
└── ollama/
    └── start.sh                    # Model pull script
```

---

## 🚀 Quick Start

See [QUICKSTART.md](QUICKSTART.md) for detailed setup instructions.

**TL;DR (Docker):**
```bash
cp .env.example .env
docker compose up --build
```
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Health: http://localhost:8000/health

---

## 🔧 Configuration

All settings via `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://...` | PostgreSQL connection |
| `OLLAMA_MODEL` | `qwen2.5:0.5b` | Default LLM model |
| `GRADING_MODE` | `single` | `crew` (multi-agent) or `single` (direct prompt) |
| `DEFAULT_EXAM_QUESTIONS` | `5` | Questions per exam |
| `GENERATOR_MODEL` | (same as OLLAMA_MODEL) | Optional generator model override |
| `MAX_RETRIES` | `3` | Retry count for LLM calls |

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/exam/start` | Start exam (topic, difficulty, category, mode, num_questions) |
| `POST` | `/exam/answer` | Submit an answer (exam_id, answer) |
| `POST` | `/exam/hint` | Request a hint for current question (exam_id) |
| `GET` | `/exam/{id}` | Get full exam state |
| `GET` | `/exams` | List all exam sessions |
| `GET` | `/topics` | Available topics, difficulties, categories, and modes |
| `GET` | `/health` | Backend + DB + Ollama health |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------:|
| Frontend | React 18, Vite 5, Lucide React |
| Backend | FastAPI, Python 3.11 |
| AI Agents | CrewAI |
| LLM | Ollama + qwen2.5:0.5b |
| Database | PostgreSQL 16 |
| Container | Docker Compose |

---

## 📄 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.
