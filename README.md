# 🗄️ SQL Database Agent

A natural language SQL agent — ask questions in plain English, get SQL queries, live results, and AI-powered explanations. Runs fully free with open-source LLMs via **Ollama** (local) or **Groq** (free cloud API).

---

## ✨ Features

- 💬 **Natural language → SQL** — type a question, get a query
- ▶️ **Live query execution** against a real SQLite database
- 🔍 **AI explanations** — results explained in plain English
- 🔁 **Self-correction** — automatically retries if the first SQL fails
- 🔐 **JWT Authentication** — login-protected API and UI
- 📊 **Schema sidebar** — live table/column reference while you chat
- 🆓 **100% free** — Ollama (local) or Groq free-tier (cloud)

---

## 🖥️ Demo

| Login | Chat Interface |
|---|---|
| Sign in with demo credentials | Ask questions, see SQL + results + explanation |

**Demo credentials:** `demo / demo123` · `admin / admin123`

---

## 🗂️ Dataset

Uses the [Chinook Database](https://github.com/lerocha/chinook-database) — a public domain music store dataset with 11 tables:

`Album` · `Artist` · `Customer` · `Employee` · `Genre` · `Invoice` · `InvoiceLine` · `MediaType` · `Playlist` · `PlaylistTrack` · `Track`

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python · FastAPI |
| LLM (local) | Ollama · `qwen2.5-coder:7b` / `phi3` |
| LLM (cloud) | Groq API · `llama-3.1-8b-instant` (free tier) |
| Database | SQLite · Chinook DB |
| Auth | JWT · `python-jose` |
| Frontend | Vanilla HTML/CSS/JS (no framework) |
| Deployment | Railway · Hugging Face Spaces · Render |

---

## 🚀 Local Setup

### Prerequisites
- Python 3.11+
- [Ollama](https://ollama.com) installed

### 1. Clone & install
```bash
git clone https://github.com/PranavDonepudi/sql-database-agent.git
cd sql-database-agent
pip install -r requirements.txt
```

### 2. Configure environment
```bash
cp .env.example .env
```

Edit `.env`:
```env
# Local (Ollama)
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5-coder:7b     # recommended for M2 Mac

# OR Cloud (Groq free tier — console.groq.com)
# LLM_PROVIDER=groq
# GROQ_API_KEY=gsk_...
# GROQ_MODEL=llama-3.1-8b-instant

SECRET_KEY=your-random-secret
DB_PATH=./data/chinook.db
```

### 3. Pull model & download database
```bash
ollama pull qwen2.5-coder:7b
python setup_db.py
```

### 4. Run
```bash
uvicorn app.main:app --reload --port 8000
```

Open [http://localhost:8000](http://localhost:8000)

---

## ☁️ Deployment

### Railway
1. Connect this repo in [railway.app](https://railway.app)
2. Set environment variables:
   ```
   LLM_PROVIDER=groq
   GROQ_API_KEY=gsk_...
   GROQ_MODEL=llama-3.1-8b-instant
   SECRET_KEY=<random string>
   DB_PATH=./data/chinook.db
   ```
3. Deploy — Railway uses `railway.toml` automatically

### Hugging Face Spaces (Docker)
1. New Space → SDK: **Docker**
2. Link this GitHub repo
3. Add the same env vars as Secrets
4. Auto-deploys on every push

### Render
1. New Web Service → connect this repo
2. Build command: `pip install -r requirements.txt && python setup_db.py`
3. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add the same env vars

---

## 📁 Project Structure

```
sql-database-agent/
├── app/
│   ├── main.py        # FastAPI routes
│   ├── agent.py       # NL→SQL pipeline + self-correction
│   ├── db.py          # SQLite query runner + schema introspection
│   ├── llm.py         # Ollama / Groq provider abstraction
│   └── auth.py        # JWT authentication
├── frontend/
│   └── index.html     # Chat UI (no framework)
├── data/              # SQLite DB downloaded here by setup_db.py
├── setup_db.py        # One-time Chinook DB download
├── requirements.txt
├── Dockerfile         # For HF Spaces / container deployment
├── Procfile           # For Render / Railway
└── railway.toml       # Railway deploy config
```

---

## 🔒 API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/login` | No | Returns JWT token |
| `POST` | `/query` | Yes | NL question → SQL + results + explanation |
| `GET` | `/schema` | Yes | Returns DB schema |
| `GET` | `/health` | No | Health check |
| `GET` | `/` | No | Serves frontend |

---

## 🔮 Roadmap

- [ ] Query history panel
- [ ] Support PostgreSQL / MySQL connections
- [ ] Export results as CSV
- [ ] Multi-database support
- [ ] Chart visualizations for numeric results

---

## 📄 License

MIT — free to use, modify, and deploy.
