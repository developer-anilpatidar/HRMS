"""Employee agent LangGraph — LLM wired, no tools yet.

Graph shape for this step:

    START → agent(Ollama) → END

Next step: add tools node + conditional edges (ReAct loop).
"""

from __future__ import annotations

import os
from typing import Annotated, TypedDict
from uuid import UUID

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from app.agents.employee.prompt import EMPLOYEE_SYSTEM_PROMPT

load_dotenv()


class EmployeeAgentState(TypedDict):
    """Shared state that flows through every node."""

    messages: Annotated[list[BaseMessage], add_messages]
    employee_id: UUID
    organization_id: UUID


def get_chat_model() -> ChatOllama:
    return ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "qwen3:4b"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0,
    )


def agent_node(state: EmployeeAgentState) -> dict:
    """Call local Ollama with the employee system prompt (no tools yet)."""
    llm = get_chat_model()
    messages = [SystemMessage(content=EMPLOYEE_SYSTEM_PROMPT), *state["messages"]]
    response = llm.invoke(messages)
    return {"messages": [response]}


def build_employee_graph():
    """Compile START → agent → END."""
    graph = StateGraph(EmployeeAgentState)

    graph.add_node("agent", agent_node)

    graph.add_edge(START, "agent")
    graph.add_edge("agent", END)

    return graph.compile()


# Module-level compiled graph for reuse
employee_graph = build_employee_graph()
