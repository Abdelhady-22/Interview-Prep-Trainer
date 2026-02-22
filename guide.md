# 🚀 VM Deployment Guide — Interview Prep Trainer

Step-by-step guide to deploy on an **Ubuntu 24.04** server (tested on DigitalOcean droplet with 4 GB RAM).

---

## Prerequisites

- Ubuntu 24.04 server with SSH access
- At least **4 GB RAM** (for Ollama + model)
- Ports **3000** and **8000** open in firewall

---

## Step 1: Connect to the VM

```bash
ssh root@<YOUR_VM_IP>
```

---

## Step 2: Install Docker

```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh

# Install Docker Compose plugin
apt install docker-compose-plugin -y

# Verify
docker --version
docker compose version
```

---

## Step 3: Install Git (if not installed)

```bash
apt install git -y
```

---

## Step 4: Clone the Project

```bash
cd /opt
git clone <YOUR_REPO_URL> interview-prep-trainer
cd interview-prep-trainer
```

Or if you're uploading manually:
```bash
# From your local machine
scp -r "d:\Interview Prep Trainer\*" root@<YOUR_VM_IP>:/opt/interview-prep-trainer/
```

---

## Step 5: Configure Environment

```bash
cp .env.example .env
nano .env
```

**Important changes for VM deployment:**
```env
# Change VITE_API_URL to your VM's public IP
VITE_API_URL=http://<YOUR_VM_IP>:8000
```

Save and exit (`Ctrl+X`, `Y`, `Enter`).

---

## Step 6: Open Firewall Ports

```bash
# If using UFW
ufw allow 3000/tcp
ufw allow 8000/tcp
ufw reload
ufw status
```

If using DigitalOcean's cloud firewall, add inbound rules for ports 3000 and 8000 in the dashboard.

---

## Step 7: Build and Start

```bash
cd /opt/interview-prep-trainer
docker compose up --build -d
```

This will:
1. Build the frontend container (React + Vite)
2. Build the backend container (FastAPI + CrewAI)
3. Start PostgreSQL
4. Start Ollama and auto-pull the `qwen2.5:0.5b` model

---

## Step 8: Monitor Startup

```bash
# Watch all logs
docker compose logs -f

# Or watch specific services
docker compose logs -f ollama    # Model download progress
docker compose logs -f backend   # Backend startup
docker compose logs -f frontend  # Frontend build
```

Wait until you see:
```
backend-1  | INFO:     Uvicorn running on http://0.0.0.0:8000
frontend-1 | VITE vX.X.X ready in XXXms
```

---

## Step 9: Verify

```bash
# Health check
curl http://localhost:8000/health
# Expected: {"backend":"ok","database":"ok","ollama":"ok"}

# Topics, categories, and modes
curl http://localhost:8000/topics
```

Open in browser:
- **Frontend**: `http://<YOUR_VM_IP>:3000`
- **Health**: `http://<YOUR_VM_IP>:8000/health`

---

## Managing the App

### Start / Stop / Restart

```bash
cd /opt/interview-prep-trainer

# Start (in background)
docker compose up -d

# Stop
docker compose down

# Restart everything
docker compose restart

# Restart just backend
docker compose restart backend

# Rebuild after code changes
docker compose up --build -d
```

### View Logs

```bash
# All services
docker compose logs -f

# Just backend
docker compose logs -f backend

# Last 100 lines of backend
docker compose logs --tail 100 backend
```

### Update Code

```bash
cd /opt/interview-prep-trainer
git pull origin main
docker compose up --build -d
```

### Reset Database

```bash
docker compose down -v    # Deletes all data
docker compose up --build -d
```

### ⚠️ Database Migration Note

The app uses SQLAlchemy's `create_all()` which **auto-creates tables** on first run. However, it does **NOT** alter existing tables when new columns are added (e.g., after upgrading to a new version with `mode`, `hints_used`, or `category` columns).

**After upgrading the app code**, if new columns were added, you must reset the database:

```bash
# ⚠️ This deletes ALL exam data!
docker compose down -v
docker compose up --build -d
```

> **When is this needed?** Only when a code update adds new columns to the database models. The app logs will show errors like `column "mode" does not exist` or `column "hints_used" does not exist` if a reset is needed.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Ollama keeps restarting | RAM too low. Check: `free -h`. Need 4+ GB |
| Backend can't connect to DB | Wait for db healthcheck: `docker compose ps` |
| Frontend shows blank page | Check `VITE_API_URL` in `.env`, rebuild frontend |
| "Connection refused" in browser | Check firewall: `ufw status`. Are ports 3000/8000 open? |
| Slow question generation | Expected with `qwen2.5:0.5b` on CPU. Upgrade model for speed |
| Out of disk space | Clean Docker: `docker system prune -af` |
| `column "xyz" does not exist` | New columns added — run `docker compose down -v && docker compose up --build` |

---

## Optional: Use a Bigger Model

For better question quality, grading accuracy, and hint generation:

```bash
# SSH into the VM
ssh root@<YOUR_VM_IP>

# Edit .env
cd /opt/interview-prep-trainer
nano .env
# Change: OLLAMA_MODEL=qwen2.5:3b

# Then rebuild
docker compose up --build -d
```

> ⚠️ Larger models need more RAM. `qwen2.5:3b` needs ~4 GB, `qwen2.5:7b` needs ~8 GB.

---

## Optional: Domain + HTTPS (Nginx)

To serve behind a domain with HTTPS:

```bash
apt install nginx certbot python3-certbot-nginx -y

# Create Nginx config
nano /etc/nginx/sites-available/interview-prep
```

```nginx
server {
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
    }

    location /exam/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }

    location /exams {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }

    location /topics {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }

    location /health {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }
}
```

```bash
ln -s /etc/nginx/sites-available/interview-prep /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
certbot --nginx -d your-domain.com
```

> **Note:** The `/exam/` Nginx location catches all exam-related routes including `/exam/start`, `/exam/answer`, `/exam/hint`, and `/exam/{id}`.
