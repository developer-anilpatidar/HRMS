"""Chat API: Employee agent with profile + leave tools."""

from fastapi import APIRouter
from langchain_core.messages import HumanMessage

from app.agents.employee.graph import build_employee_graph
from app.agents.employee.tools import build_employee_tools
from app.api.deps import CurrentEmployee, DbSession
from app.schemas.chat import ChatIn, ChatOut

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatOut)
def chat(payload: ChatIn, db: DbSession, employee: CurrentEmployee) -> ChatOut:
    """Send one message to the Employee agent."""
    tools = build_employee_tools(db, employee.id, employee.organization_id)
    graph = build_employee_graph(tools)

    result = graph.invoke(
        {
            "messages": [HumanMessage(content=payload.message)],
            "employee_id": employee.id,
            "organization_id": employee.organization_id,
        }
    )
    reply = result["messages"][-1].content
    if not isinstance(reply, str):
        reply = str(reply)

    return ChatOut(
        reply=reply,
        employee_id=str(employee.id),
        employee_email=employee.work_email,
    )
