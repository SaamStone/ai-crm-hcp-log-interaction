from typing import Any, Optional

from pydantic import BaseModel, Field


class FormState(BaseModel):
    """Mirrors the Log HCP Interaction form on the frontend. Every field is optional
    because the form fills in progressively as the conversation with the AI Assistant
    develops."""

    hcp_name: Optional[str] = None
    interaction_type: Optional[str] = "Meeting"
    date: Optional[str] = None
    time: Optional[str] = None
    attendees: Optional[str] = None
    topics_discussed: Optional[str] = None
    materials_shared: list[str] = Field(default_factory=list)
    samples_distributed: list[str] = Field(default_factory=list)
    sentiment: Optional[str] = None
    outcomes: Optional[str] = None
    follow_up_actions: Optional[str] = None


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    session_id: str
    message: str
    form_state: FormState


class ToolTrace(BaseModel):
    tool: str
    args: dict[str, Any]
    result_summary: str


class ChatResponse(BaseModel):
    reply: str
    form_state: FormState
    changed_fields: list[str] = Field(default_factory=list)
    tool_calls: list[ToolTrace] = Field(default_factory=list)


class InteractionCreate(FormState):
    pass


class InteractionOut(FormState):
    id: int

    class Config:
        from_attributes = True


class HCPOut(BaseModel):
    id: int
    name: str
    specialty: Optional[str] = None
    hospital: Optional[str] = None

    class Config:
        from_attributes = True
