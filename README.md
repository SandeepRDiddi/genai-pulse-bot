# 🤖 GenAI Pulse Bot

> Stay up to date with the latest in Generative AI — automatically.

[![License: MIT](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue?style=flat-square)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?style=flat-square)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/docker-ready-blue?style=flat-square)](Dockerfile)

GenAI Pulse Bot automatically tracks the latest developments in Generative AI from **Arxiv**, **HuggingFace**, **Reddit**, and **Tech News** — and delivers them to you via a beautiful web dashboard, Telegram, Slack, or email.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📄 **Arxiv Papers** | Latest AI/ML papers (cs.AI, cs.LG, cs.CL, cs.CV) |
| 🤗 **HuggingFace** | Trending models + HF Daily Papers |
| 💬 **Reddit** | Hot posts from r/MachineLearning, r/LocalLLaMA, r/artificial |
| 📰 **Tech News** | AI news from TechCrunch, VentureBeat, MIT Tech Review, The Verge |
| 🌐 **Web Dashboard** | Real-time filterable feed with search |
| 📱 **Telegram** | Daily digest to your channel |
| 💬 **Slack** | Rich Block Kit messages to your workspace |
| 📧 **Email** | Beautiful HTML digest to subscribers |
| ⏰ **Scheduled** | Auto-fetches every 6 hours via Celery |
| 🐳 **Docker** | One-command deployment |

---

## 🚀 Quick Start

### Option 1: Local (no Docker)

```bash
# Clone
git clone https://github.com/SandeepRDiddi/genai-pulse-bot.git
cd genai-pulse-bot

# Install
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your API keys (only add what you need)

# Run
uvicorn app.main:app --reload --port 8000
```

Open **http://localhost:8000** — the dashboard loads immediately.

To trigger a fetch manually:
```bash
curl -X POST http://localhost:8000/api/admin/fetch
```

### Option 2: Docker (recommended)

```bash
git clone https://github.com/SandeepRDiddi/genai-pulse-bot.git
cd genai-pulse-bot
cp .env.example .env   # edit with your keys

docker-compose up -d
```

This starts:
- **API** on port 8000
- **Celery Worker** (background tasks)
- **Celery Beat** (scheduler)
- **Redis** (message broker)

---

## ⚙️ Configuration

Copy `.env.example` to `.env` — everything is optional except what you want to use:

```env
# Required for scheduled tasks
REDIS_URL=redis://localhost:6379/0

# Optional notifiers — add only what you want
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHANNEL_ID=@your_channel

SLACK_BOT_TOKEN=xoxb-your-token
SLACK_CHANNEL=#genai-updates

SMTP_USER=your@gmail.com
SMTP_PASSWORD=your_app_password
```

The web dashboard works with **zero configuration** — no API keys needed.

---

## 🌐 Deploy to Railway (Free)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/genai-pulse)

1. Click the button above
2. Add your environment variables
3. Deploy — Railway gives you a public URL

### Or deploy manually:
```bash
npm install -g @railway/cli
railway login
railway up
```

---

## 📡 API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/articles` | GET | Get latest articles (filter by `source`, `category`, `hours`) |
| `/api/stats` | GET | Get counts by source and category |
| `/api/subscribe` | POST | Subscribe to email digest |
| `/api/admin/fetch` | POST | Manually trigger scraping |
| `/api/admin/digest` | POST | Manually send digest |
| `/api/health` | GET | Health check |

**Example:**
```bash
# Get last 24h Arxiv papers
curl "http://localhost:8000/api/articles?source=arxiv&hours=24"

# Get stats
curl "http://localhost:8000/api/stats"
```

---

## 🤖 Setting Up Telegram Bot

1. Message [@BotFather](https://t.me/botfather) → `/newbot` → copy token
2. Create a Telegram channel
3. Add your bot as admin to the channel
4. Get channel ID from [@userinfobot](https://t.me/userinfobot)
5. Add to `.env`:
   ```
   TELEGRAM_BOT_TOKEN=your_token
   TELEGRAM_CHANNEL_ID=@your_channel
   ```

---

## 💬 Setting Up Slack Bot

1. Go to [api.slack.com/apps](https://api.slack.com/apps) → Create New App
2. Add OAuth scopes: `chat:write`, `channels:join`
3. Install to workspace → copy **Bot Token**
4. Invite bot to your channel: `/invite @your-bot`
5. Add to `.env`:
   ```
   SLACK_BOT_TOKEN=xoxb-your-token
   SLACK_CHANNEL=#genai-updates
   ```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│                 GenAI Pulse Bot              │
├──────────────┬──────────────────────────────┤
│   Scrapers   │  Notifiers                   │
│  ─────────   │  ──────────                  │
│  Arxiv API   │  Telegram Bot                │
│  HF Hub API  │  Slack Block Kit             │
│  Reddit JSON │  Email (SMTP)                │
│  RSS Feeds   │  Web Dashboard               │
├──────────────┴──────────────────────────────┤
│   FastAPI + SQLAlchemy + Celery + Redis      │
└─────────────────────────────────────────────┘
```

---

## 🤝 Contributing

Contributions welcome! Ideas for new features:
- [ ] Twitter/X integration
- [ ] GitHub Trending repos
- [ ] AI-powered weekly summary (using Claude/GPT)
- [ ] Discord bot notifier
- [ ] Mobile app (React Native)
- [ ] RSS feed output

Open an issue or PR!

---

## 📄 License

MIT — free to use, modify, and deploy.

---

Built with ❤️ by [@SandeepRDiddi](https://github.com/SandeepRDiddi)
