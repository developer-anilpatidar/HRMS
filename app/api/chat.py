"""Chat API: Employee agent with profile + leave tools and Postgres memory."""

from uuid import uuid4

from fastapi import APIRouter
from langchain_core.messages import HumanMessage

from app.agents.checkpoint import get_checkpointer
from app.agents.employee.graph import build_employee_graph
from app.agents.employee.tools import build_employee_tools
from app.api.deps import CurrentEmployee, DbSession
from app.schemas.chat import ChatIn, ChatOut

router = APIRouter(tags=["chat"])


def _langgraph_thread_id(employee_id, client_thread_id: str) -> str:
    """Namespace threads by employee so threads cannot be shared across users."""
    return f"emp:{employee_id}:{client_thread_id}"


@router.post("/chat", response_model=ChatOut)
def chat(payload: ChatIn, db: DbSession, employee: CurrentEmployee) -> ChatOut:
    """Send one message to the Employee agent (multi-turn via thread_id)."""
    thread_id = payload.thread_id or str(uuid4())
    tools = build_employee_tools(db, employee.id, employee.organization_id)
    graph = build_employee_graph(tools, checkpointer=get_checkpointer())

    result = graph.invoke(
        {
            "messages": [HumanMessage(content=payload.message)],
            "employee_id": employee.id,
            "organization_id": employee.organization_id,
        },
        config={
            "configurable": {
                "thread_id": _langgraph_thread_id(employee.id, thread_id),
            }
        },
    )
    reply = result["messages"][-1].content
    if not isinstance(reply, str):
        reply = str(reply)

    return ChatOut(
        reply=reply,
        thread_id=thread_id,
        employee_id=str(employee.id),
        employee_email=employee.work_email,
    )
