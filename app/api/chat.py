"""Chat API: Employee agent with profile + leave tools and Postgres memory."""

from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, status
from langchain_core.messages import AIMessage, HumanMessage
from sqlalchemy import text

from app.agents.checkpoint import get_checkpointer
from app.agents.employee.graph import build_employee_graph
from app.agents.employee.tools import build_employee_tools
from app.api.deps import CurrentEmployee, DbSession
from app.schemas.chat import (
    ChatIn,
    ChatMessageOut,
    ChatOut,
    ChatThreadDetailOut,
    ChatThreadOut,
)

router = APIRouter(tags=["chat"])


def _langgraph_thread_id(employee_id: UUID, client_thread_id: str) -> str:
    """Namespace threads by employee so threads cannot be shared across users."""
    return f"emp:{employee_id}:{client_thread_id}"


def _client_thread_id(employee_id: UUID, langgraph_thread_id: str) -> str | None:
    prefix = f"emp:{employee_id}:"
    if not langgraph_thread_id.startswith(prefix):
        return None
    return langgraph_thread_id[len(prefix) :]


def _message_content(content: object) -> str:
    if isinstance(content, str):
        return content
    return str(content)


def _ui_messages_from_checkpoint(messages: list) -> list[ChatMessageOut]:
    out: list[ChatMessageOut] = []
    for message in messages:
        msg_type = getattr(message, "type", None)
        if msg_type == "human" or isinstance(message, HumanMessage):
            out.append(
                ChatMessageOut(role="user", content=_message_content(message.content))
            )
        elif msg_type == "ai" or isinstance(message, AIMessage):
            # Skip pure tool-call turns with empty visible text when possible
            text = _message_content(message.content).strip()
            if text:
                out.append(ChatMessageOut(role="assistant", content=text))
    return out


@router.get("/chat/threads", response_model=list[ChatThreadOut])
def list_chat_threads(db: DbSession, employee: CurrentEmployee) -> list[ChatThreadOut]:
    """List conversation threads for the current employee."""
    prefix = f"emp:{employee.id}:"
    rows = db.execute(
        text(
            """
            SELECT thread_id, MAX(checkpoint_id) AS last_checkpoint_id
            FROM checkpoints
            WHERE thread_id LIKE :prefix
            GROUP BY thread_id
            ORDER BY MAX(checkpoint_id) DESC
            """
        ),
        {"prefix": f"{prefix}%"},
    ).fetchall()

    checkpointer = get_checkpointer()
    threads: list[ChatThreadOut] = []
    for row in rows:
        client_id = _client_thread_id(employee.id, row.thread_id)
        if not client_id:
            continue
        tup = checkpointer.get_tuple({"configurable": {"thread_id": row.thread_id}})
        messages = []
        if tup is not None:
            messages = tup.checkpoint.get("channel_values", {}).get("messages", [])
        ui_messages = _ui_messages_from_checkpoint(messages)
        title = next(
            (m.content for m in ui_messages if m.role == "user"),
            "New chat",
        )
        if len(title) > 60:
            title = title[:57] + "..."
        threads.append(
            ChatThreadOut(
                thread_id=client_id,
                title=title,
                message_count=len(ui_messages),
                updated_at=str(row.last_checkpoint_id) if row.last_checkpoint_id else None,
            )
        )
    return threads


@router.get("/chat/threads/{thread_id}", response_model=ChatThreadDetailOut)
def get_chat_thread(
    thread_id: str,
    employee: CurrentEmployee,
) -> ChatThreadDetailOut:
    """Load messages for one conversation thread."""
    langgraph_id = _langgraph_thread_id(employee.id, thread_id)
    tup = get_checkpointer().get_tuple({"configurable": {"thread_id": langgraph_id}})
    if tup is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat thread not found",
        )
    messages = tup.checkpoint.get("channel_values", {}).get("messages", [])
    return ChatThreadDetailOut(
        thread_id=thread_id,
        messages=_ui_messages_from_checkpoint(messages),
    )


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
