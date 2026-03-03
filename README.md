# GenAI Global Trends Bot (Open-Source)

A self-hosted “stay up-to-date on GenAI” bot with **global coverage** beyond RSS.

## What it does
- **Collects global news + research signals** from:
  - **GDELT DOC API** (global news)  
  - **Media Cloud API v2** (online news archive / story stream)
  - Optional RSS feeds (blogs, arXiv RSS, etc.)
- **Normalizes + deduplicates** items (URL + title hashing)
- **Indexes** into **Qdrant** vector DB using local embeddings
- **Answers questions** with citations via any **OpenAI-compatible** LLM endpoint (Ollama supported)
- Produces **persona briefings**:
  - `Leadership` (what changed, why it matters, actions, risks)
  - `Business` (use cases, value, adoption, vendors, risks)
  - `Tech` (architectures, evals, OSS, implementation notes)

---

## Quickstart

### Prereqs
- Python 3.10+
- Docker + Docker Compose

### 1) Start Qdrant
```bash
docker compose up -d qdrant
```

### 2) Install + configure
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

### 3) Ingest fresh items (GDELT + MediaCloud + RSS)
```bash
python -m app.ingest --once
```

### 4) Run API + UI
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
streamlit run ui/streamlit_app.py
```

Open:
- API docs: http://localhost:8000/docs
- UI: http://localhost:8501

---

## LLM Configuration (Ollama or OpenAI-Compatible)

This app calls an **OpenAI-compatible** Chat Completions endpoint.

### Option A: Local (Ollama)
```bash
ollama pull llama3.1
```
Set in `.env`:
- `LLM_BASE_URL=http://localhost:11434/v1`
- `LLM_API_KEY=ollama`  (any string)
- `LLM_MODEL=llama3.1`

### Option B: Cloud (OpenAI-compatible)
Set:
- `LLM_BASE_URL=https://api.openai.com/v1`
- `LLM_API_KEY=...`
- `LLM_MODEL=...`

---

## API Endpoints
- `POST /chat` — Q&A with citations
- `GET /briefing/leadership` — latest leadership briefing
- `GET /briefing/business` — latest business briefing
- `GET /briefing/tech` — latest technical briefing

---

## Source Keys / Limits
### Media Cloud
You need an API key (see Media Cloud docs). The API uses a `key` query parameter and has request limits.  
Set `MEDIACLOUD_API_KEY` in `.env`.

### GDELT
No key is required for typical DOC queries, but it has rate limits; keep ingestion modest.

---

## GitHub Push (you run this)
I can’t directly push to your GitHub from here. After unzipping:

```bash
git init
git add .
git commit -m "Initial commit: GenAI Global Trends Bot"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

---

## Project Layout
```
genai-tech-bot/
  app/
    providers/          # GDELT, MediaCloud, RSS
    ingest.py           # ingestion runner
    retrieval.py        # Qdrant search
    briefing.py         # persona briefing generator
    main.py             # FastAPI endpoints
  ui/
    streamlit_app.py
  docker-compose.yml
```
