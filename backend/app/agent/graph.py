from langchain_core.messages import SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

from .state import AgentState

SYSTEM_PROMPT = """You are the AI Assistant embedded in the "Log HCP Interaction" \
screen of a pharmaceutical CRM. You act as an experienced field-operations \
copilot for a pharma sales representative.

The rep NEVER fills the form on the left manually - every field is populated \
or corrected exclusively through your tool calls. This means:
- Whenever the user describes a new interaction, call `log_interaction` to \
  extract and fill fields. Do not guess values they did not mention.
- Whenever the user corrects/updates something already logged, call \
  `edit_interaction` passing ONLY the fields that changed.
- Use `lookup_hcp` to validate/resolve an HCP's name against the directory.
- Use `manage_materials_samples` whenever materials or samples are mentioned.
- Use `suggest_follow_up` when asked for a suggestion or when the user agrees \
  to your offer of one.
- You may call more than one tool for a single message if it naturally \
  contains both new information and a correction, or a name that needs \
  lookup plus new details.
- After calling tool(s), reply to the user in 1-3 short, friendly sentences \
  confirming what was updated. Do not restate the entire form back to them \
  field by field - just summarize plainly. If it fits, offer one relevant \
  next step (e.g. suggesting a follow-up), but do not be pushy.
- If the message has no loggable/editable content, just answer conversationally \
  without calling a tool.
"""


def build_graph(tools: list, model_name: str, api_key: str):
    llm = ChatGroq(model=model_name, api_key=api_key, temperature=0.1)
    llm_with_tools = llm.bind_tools(tools)

    def agent_node(state: AgentState):
        messages = state["messages"]
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    def route(state: AgentState):
        last = state["messages"][-1]
        if getattr(last, "tool_calls", None):
            return "tools"
        return END

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(tools))
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", route, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")
    return graph.compile()
