"""Basic chat API: START → LLM → END (no tools yet)."""

from fastapi import APIRouter
from langchain_core.messages import HumanMessage

from app.agents.employee.graph import employee_graph
from app.api.deps import CurrentEmployee
from app.schemas.chat import ChatIn, ChatOut

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatOut)
def chat(payload: ChatIn, employee: CurrentEmployee) -> ChatOut:
    """Send one message to the Employee agent"""
    result = employee_graph.invoke(
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
