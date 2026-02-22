# ⚡ QUICKSTART — Interview Prep Trainer

Two ways to run: **Docker** (recommended) or **Manual** (without Docker).

---

## Option 1: Docker (Recommended)

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- At least **4 GB RAM** allocated to Docker (for the Ollama model)

### Steps

**1. Clone / navigate to the project:**
```bash
cd "Interview Prep Trainer"
```

**2. Create your environment file:**
```bash
cp .env.example .env
```

**3. Build and start all containers:**
```bash
docker compose up --build
```

**4. Wait for Ollama to pull the model** (first run only, ~400 MB):
```
ollama-1  | Pulling model: qwen2.5:0.5b (this may take a while on first run)...
ollama-1  | Model qwen2.5:0.5b pulled successfully!
```

**5. Open the app:**
- 🌐 Frontend: [http://localhost:3000](http://localhost:3000)
- 🔌 Backend API: [http://localhost:8000](http://localhost:8000)
- 💚 Health check: [http://localhost:8000/health](http://localhost:8000/health)

### Docker Commands Cheat Sheet

| Command | What it does |
|---------|-------------|
| `docker compose up --build` | Build & start all containers |
| `docker compose up -d` | Start in background (detached) |
| `docker compose down` | Stop all containers |
| `docker compose down -v` | Stop & delete all data (volumes) |
| `docker compose logs -f backend` | Follow backend logs |
| `docker compose logs -f ollama` | Follow Ollama logs (model pull progress) |
| `docker compose restart backend` | Restart just the backend |
| `docker compose ps` | See container status |

---

## Option 2: Manual (Without Docker)

### Prerequisites
- **Python 3.11+** — [python.org](https://www.python.org/downloads/)
- **Node.js 18+** — [nodejs.org](https://nodejs.org/)
- **PostgreSQL 16** — [postgresql.org](https://www.postgresql.org/download/)
- **Ollama** — [ollama.com](https://ollama.com/download)

### Step 1: Start PostgreSQL

Make sure PostgreSQL is running and create the database:

```sql
-- Connect to psql as superuser
CREATE USER grader WITH PASSWORD 'graderpass';
CREATE DATABASE examgrader OWNER grader;
```

### Step 2: Start Ollama and Pull the Model

```bash
# Start Ollama server (if not already running)
ollama serve

# In another terminal, pull the model
ollama pull qwen2.5:0.5b
```

### Step 3: Start the Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=postgresql://grader:graderpass@localhost:5432/examgrader
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_MODEL=qwen2.5:0.5b
export GRADING_MODE=single
export DEFAULT_EXAM_QUESTIONS=5

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 4: Start the Frontend

Open a **new terminal**:

```bash
cd frontend

# Install dependencies
npm install

# Set the backend URL
export VITE_API_URL=http://localhost:8000

# Start the dev server
npm run dev
```

Open: [http://localhost:3000](http://localhost:3000)

---

## 🧪 Test the API Manually

### Health Check
```bash
curl http://localhost:8000/health
```
Expected: `{"backend":"ok","database":"ok","ollama":"ok"}`

### Get Available Topics, Categories & Modes
```bash
curl http://localhost:8000/topics
```

### Start an Exam (Practice Mode)
```bash
curl -X POST http://localhost:8000/exam/start \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "python",
    "difficulty": "easy",
    "num_questions": 3,
    "question_type": "written",
    "category": "concept",
    "mode": "practice"
  }'
```

### Start an Exam (Timed Mode)
```bash
curl -X POST http://localhost:8000/exam/start \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "data_structures",
    "difficulty": "medium",
    "num_questions": 5,
    "question_type": "multiple_choice",
    "category": "coding",
    "mode": "timed"
  }'
```

### Submit an Answer
```bash
curl -X POST http://localhost:8000/exam/answer \
  -H "Content-Type: application/json" \
  -d '{
    "exam_id": "<EXAM_ID_FROM_ABOVE>",
    "answer": "A list is mutable, a tuple is immutable"
  }'
```

### Request a Hint (Practice/Mock modes only)
```bash
curl -X POST http://localhost:8000/exam/hint \
  -H "Content-Type: application/json" \
  -d '{
    "exam_id": "<EXAM_ID_FROM_ABOVE>"
  }'
```

### List All Exams
```bash
curl http://localhost:8000/exams
```

---

## ⚙️ Configuration Reference

| Variable | Default | When to Change |
|----------|---------|---------------|
| `DATABASE_URL` | `postgresql://...@db:5432/...` | Change `db` to `localhost` without Docker |
| `OLLAMA_BASE_URL` | `http://ollama:11434` | Change `ollama` to `localhost` without Docker |
| `OLLAMA_MODEL` | `qwen2.5:0.5b` | Use a larger model for better quality (e.g., `qwen2.5:3b`) |
| `GRADING_MODE` | `single` | Set to `crew` for multi-agent grading (slower but richer) |
| `DEFAULT_EXAM_QUESTIONS` | `5` | Number of questions per exam |

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| `ollama` container keeps restarting | Wait — it's pulling the model. Check: `docker compose logs -f ollama` |
| `backend` can't connect to `db` | Make sure PostgreSQL container is healthy: `docker compose ps` |
| Frontend shows "Failed to fetch" | Backend not running or CORS issue. Check `VITE_API_URL` |
| Grading returns 500 | LLM failed to produce valid JSON. Try a larger model |
| Port 3000/8000 already in use | Stop the conflicting process or change ports |
| Questions are low quality | Upgrade from `qwen2.5:0.5b` to `qwen2.5:3b` or larger |
| `column "xyz" does not exist` | New columns added — run `docker compose down -v && docker compose up --build` |

---

## ⚠️ Database Migration Note

The app uses SQLAlchemy's `create_all()` which auto-creates tables on first run but does **NOT** alter existing tables when new columns are added. After upgrading the app, if you see errors like `column "mode" does not exist` or `column "hints_used" does not exist`, you must reset the database:

```bash
# ⚠️ This deletes ALL exam data!
docker compose down -v
docker compose up --build -d
```
