# 🧠 AI-First HCP CRM — Log Interaction Module

> A pharmaceutical CRM screen where a **sales rep never fills the form manually** — every field is populated, corrected, and managed exclusively through a **natural-language AI chat assistant** powered by **LangGraph + Groq**.

![Split Screen](https://img.shields.io/badge/Layout-Split%20Screen-blue) ![LangGraph](https://img.shields.io/badge/Agent-LangGraph-orange) ![Groq](https://img.shields.io/badge/LLM-Groq%20llama--3.3--70b-green) ![FastAPI](https://img.shields.io/badge/Backend-FastAPI-teal) ![React](https://img.shields.io/badge/Frontend-React%2019-blue)

---

## 🖥️ What It Does

This is a **split-screen CRM module** with two panels:

| Left Panel | Right Panel |
|---|---|
| **Interaction Detail Form** — HCP name, type, date, time, attendees, topics, materials, samples, sentiment, outcomes, follow-up | **AI Assistant Chat** — Natural language interface that drives the form |

**The golden rule:** The rep **never touches the form directly**. Every field is filled, corrected, and managed via the AI assistant on the right.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 19, Redux Toolkit, Vite |
| **Backend** | FastAPI, SQLAlchemy, SQLite (swappable to Postgres/MySQL) |
| **AI Agent** | LangGraph (ReAct graph), LangChain Groq |
| **LLM** | Groq — `llama-3.3-70b-versatile` |
| **Session State** | In-memory per-session conversation history |

---

## 🚀 Quick Start (Recommended)

### Step 1 — Clone the repo

```bash
git clone https://github.com/SaamStone/ai-crm-hcp-log-interaction.git
cd ai-crm-hcp-log-interaction
```

### Step 2 — Get a free Groq API key

Sign up at **https://console.groq.com/keys** and create an API key. It's free.

### Step 3 — Configure the backend

```bash
# Windows
cd backend
copy .env.example .env
```

```bash
# Mac / Linux
cd backend
cp .env.example .env
```

Now open `backend/.env` in any text editor and replace `your_groq_api_key_here` with your real key:

```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxx
GROQ_MODEL=llama-3.3-70b-versatile
DATABASE_URL=sqlite:///./hcp_crm.db
CORS_ORIGINS=http://localhost:5173
```

### Step 4 — Install backend dependencies

```bash
# From the backend/ directory
pip install -r requirements.txt
```

### Step 5 — Install frontend dependencies

```bash
# From the frontend/ directory
cd ../frontend
npm install
```

### Step 6 — Run both servers

Open **two separate terminals**:

**Terminal 1 — Backend:**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

### Step 7 — Open the app

Open **http://localhost:5173** in your browser. ✅

> ⚠️ Do **not** open http://localhost:8000 — that is the API server, not the UI.

---

## 📋 Prerequisites

| Tool | Minimum Version | Download |
|---|---|---|
| Python | 3.10+ | https://python.org |
| Node.js | 18+ | https://nodejs.org |
| npm | comes with Node.js | — |
| Groq API key | free | https://console.groq.com/keys |

---

## 💬 Example Prompts to Try

```
"Met Dr. John Smith at Apollo Hospitals today, discussed Cardizem dosing,
he was very interested, shared the efficacy brochure and left 3 sample packs.
Positive sentiment overall."

"Actually, sorry — the sentiment was neutral, not positive."

"What follow-up should I schedule?"

"Also add a Metformin sample to the record."
```

---

## 🔧 The 5 LangGraph Tools

All tools are defined in `backend/app/agent/tools.py` and wired into a **LangGraph StateGraph** in `backend/app/agent/graph.py`.

| Tool | Purpose |
|---|---|
| `log_interaction` | Extract every field from a free-text description and populate the form |
| `edit_interaction` | Correct specific fields without touching the rest |
| `lookup_hcp` | Fuzzy-match & validate HCP names against the directory |
| `manage_materials_samples` | Track brochures, leave-behinds and drug samples |
| `suggest_follow_up` | Generate a smart next-best-action recommendation |

---

## 📁 Project Structure

```
hcp-crm/
├── backend/
│   ├── app/
│   │   ├── agent/
│   │   │   ├── graph.py        # LangGraph StateGraph definition
│   │   │   ├── tools.py        # All 5 LangGraph tools
│   │   │   └── state.py        # AgentState schema
│   │   ├── main.py             # FastAPI app & /api/chat endpoint
│   │   ├── models.py           # SQLAlchemy models
│   │   ├── schemas.py          # Pydantic schemas (FormState, ChatRequest, etc.)
│   │   ├── config.py           # Settings (reads .env)
│   │   ├── database.py         # DB engine & session
│   │   └── seed.py             # Sample HCP directory data
│   ├── requirements.txt
│   └── .env.example            # ← copy this to .env and add your API key
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── LogInteractionForm.jsx   # Left panel — read-only form
    │   │   └── AIAssistantPanel.jsx     # Right panel — chat interface
    │   ├── store/
    │   │   ├── chatSlice.js             # Redux chat state
    │   │   ├── interactionSlice.js      # Redux form state
    │   │   └── store.js                 # Redux store
    │   ├── api/client.js                # Axios API calls
    │   ├── App.jsx                      # Root layout (split screen)
    │   └── index.css                    # Full UI styles
    ├── package.json
    └── vite.config.js
```

---

## 🔑 Environment Variables

| Variable | Description | Default |
|---|---|---|
| `GROQ_API_KEY` | Your Groq API key — **required** | — |
| `GROQ_MODEL` | Groq model to use | `llama-3.3-70b-versatile` |
| `DATABASE_URL` | SQLAlchemy DB URL | `sqlite:///./hcp_crm.db` |
| `CORS_ORIGINS` | Allowed frontend origins | `http://localhost:5173` |

---

## 🐛 Troubleshooting

| Problem | Fix |
|---|---|
| `{"detail":"Not Found"}` in browser | You opened port 8000. Open **http://localhost:5173** instead |
| `GROQ_API_KEY is not set` error | You forgot to create `backend/.env` — copy from `.env.example` and add your key |
| `500 Internal Server Error` on chat | Check that your Groq API key is valid at https://console.groq.com/keys |
| Frontend shows blank page | Make sure `npm install` was run in the `frontend/` directory |
| Port already in use | Kill the existing process or use a different port |

---

## 📄 License

MIT
