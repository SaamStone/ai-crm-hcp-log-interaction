from collections import defaultdict

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from sqlalchemy.orm import Session

from .agent.graph import build_graph
from .agent.tools import build_tools
from .config import settings
from .database import Base, engine, get_db
from .models import HCP, Interaction
from .schemas import (ChatRequest, ChatResponse, FormState, HCPOut,
                       InteractionCreate, InteractionOut, ToolTrace)
from .seed import seed_hcps

app = FastAPI(title="AI-First HCP CRM API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Per-session in-memory conversation history. In production this would live in
# Redis/DB keyed by user session, but for this assignment a process-local dict
# is sufficient and keeps the project runnable with zero extra infra.
SESSIONS: dict[str, list] = defaultdict(list)
MAX_HISTORY_MESSAGES = 40


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    seed_hcps(db)


@app.get("/api/health")
def health():
    return {"status": "ok", "model": settings.GROQ_MODEL}


@app.get("/api/hcps", response_model=list[HCPOut])
def list_hcps(db: Session = Depends(get_db)):
    return db.query(HCP).all()


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    if not settings.GROQ_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY is not set on the server. Add it to backend/.env",
        )

    form = req.form_state.model_dump()
    changed: list[str] = []
    hcp_directory = [
        {"name": h.name, "specialty": h.specialty, "hospital": h.hospital}
        for h in db.query(HCP).all()
    ]

    tools = build_tools(form, changed, hcp_directory)
    graph = build_graph(tools, settings.GROQ_MODEL, settings.GROQ_API_KEY)

    history = SESSIONS[req.session_id][-MAX_HISTORY_MESSAGES:]
    input_messages = history + [HumanMessage(content=req.message)]
    start_len = len(input_messages)

    result = graph.invoke({"messages": input_messages})
    all_messages = result["messages"]
    new_messages = all_messages[start_len:]

    SESSIONS[req.session_id] = all_messages[-MAX_HISTORY_MESSAGES:]

    # Build a trace of every tool call made this turn (for transparency / demo).
    tool_calls_by_id = {}
    for m in new_messages:
        if isinstance(m, AIMessage) and getattr(m, "tool_calls", None):
            for tc in m.tool_calls:
                tool_calls_by_id[tc["id"]] = {"tool": tc["name"], "args": tc["args"]}

    trace: list[ToolTrace] = []
    for m in new_messages:
        if isinstance(m, ToolMessage):
            info = tool_calls_by_id.get(m.tool_call_id, {"tool": m.name, "args": {}})
            trace.append(ToolTrace(tool=info["tool"], args=info["args"], result_summary=str(m.content)))

    final_ai = next((m for m in reversed(new_messages) if isinstance(m, AIMessage) and m.content), None)
    reply = final_ai.content if final_ai else "Done."

    return ChatResponse(
        reply=reply,
        form_state=FormState(**form),
        changed_fields=list(dict.fromkeys(changed)),
        tool_calls=trace,
    )


@app.post("/api/interactions", response_model=InteractionOut)
def save_interaction(payload: InteractionCreate, db: Session = Depends(get_db)):
    row = Interaction(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@app.get("/api/interactions", response_model=list[InteractionOut])
def list_interactions(db: Session = Depends(get_db)):
    return db.query(Interaction).order_by(Interaction.id.desc()).all()
