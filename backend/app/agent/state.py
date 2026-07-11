from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """The state threaded through the LangGraph graph for one chat turn.
    `messages` holds the running conversation (human / ai / tool messages);
    LangGraph's `add_messages` reducer appends new messages instead of overwriting.
    """

    messages: Annotated[list, add_messages]
