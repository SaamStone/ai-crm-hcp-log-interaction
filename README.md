# 🧠 AI-First HCP CRM — Log Interaction Module

> A pharmaceutical CRM screen where a **sales rep never fills the form manually** — every field is populated, corrected, and managed exclusively through a **natural-language AI chat assistant** powered by **LangGraph + Groq**.

![Split Screen](https://img.shields.io/badge/Layout-Split%20Screen-blue) ![LangGraph](https://img.shields.io/badge/Agent-LangGraph-orange) ![Groq](https://img.shields.io/badge/LLM-Groq%20gemma2--9b--it-green) ![FastAPI](https://img.shields.io/badge/Backend-FastAPI-teal) ![React](https://img.shields.io/badge/Frontend-React%2019-blue)

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
| **LLM** | Groq — `gemma2-9b-it` |
| **Session State** | In-memory per-session conversation history |

---

## 🔧 The 5 LangGraph Tools

All tools are defined in `backend/app/agent/tools.py` and wired into a **LangGraph StateGraph** in `backend/app/agent/graph.py`.

### 1. `log_interaction` — *Fill form from natural language*
Extracts every field from a free-text description of a visit or call and populates the form automatically. Never invents data — only fills what the user actually mentioned.

> **Example:** *"Met Dr. Priya Rao yesterday at 3pm, discussed Insulin therapy, she was very receptive"*

---

### 2. `edit_interaction` — *Correct specific fields without touching the rest*
When the rep spots a mistake, they tell the AI in plain English. The tool updates **only** the named fields and leaves everything else exactly as it was.

> **Example:** *"Sorry, the name was actually John and the sentiment was negative"*

---

### 3. `lookup_hcp` — *Validate & auto-correct HCP names*
Fuzzy-matches a (possibly misspelled) name against the HCP master directory and sets the canonical, correctly-spelled name in the form. Asks the rep to disambiguate if multiple matches exist.

> **Example:** *"Was it Dr. Prya Rao from Care Hospitals?"*

---

### 4. `manage_materials_samples` — *Track materials & samples*
Appends brochures, leave-behind literature, and drug sample distributions to the interaction record. Items are only ever added — never overwritten or removed.

> **Example:** *"I also left a Cardizem brochure and gave 2 sample packs of Metformin"*

---

### 5. `suggest_follow_up` — *AI-generated next-best-action*
Writes a smart follow-up recommendation into the Follow-up Actions field, adapting its suggestion based on the captured sentiment and discussion topics.

- **Positive sentiment** → Schedule a follow-up meeting within 2 weeks
- **Negative sentiment** → Escalate to Medical Affairs
- **Neutral sentiment** → Send follow-up email with supporting literature

> **Example:** *"What should I do next?"*

---

## 🚀 Setup & Running

### Prerequisites
- Python 3.10+
- Node.js 18+
- A [Groq API key](https://console.groq.com/keys)

---

### Backend Setup

```bash
cd backend

# 1. Create and activate virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create your .env file
cp .env.example .env
# Edit .env and add your Groq API key:
# GROQ_API_KEY=your_key_here

# 4. Start the backend server
uvicorn app.main:app --reload --port 8000
```

Backend will be live at **http://localhost:8000**
- API docs: **http://localhost:8000/docs**

---

### Frontend Setup

```bash
cd frontend

# 1. Install dependencies
npm install

# 2. Start the dev server
npm run dev
```

Frontend will be live at **http://localhost:5173**

---

### Running End-to-End

1. Start the **backend** in one terminal (`uvicorn app.main:app --reload --port 8000`)
2. Start the **frontend** in another terminal (`npm run dev`)
3. Open **http://localhost:5173** in your browser
4. Use the **AI Assistant** panel on the right to describe an HCP interaction
5. Watch the **form on the left** fill itself automatically!

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
│   └── .env.example
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
| `GROQ_API_KEY` | Your Groq API key (required) | — |
| `GROQ_MODEL` | Groq model to use | `gemma2-9b-it` |
| `DATABASE_URL` | SQLAlchemy DB URL | `sqlite:///./hcp_crm.db` |
| `CORS_ORIGINS` | Allowed frontend origins | `http://localhost:5173` |

---

## 📄 License
MIT
