"""Employee agent LangGraph.

With profile tools:

    START → agent ⇄ tools → END

Without tools (fallback):

    START → agent → END
"""

from __future__ import annotations

import os
from typing import Annotated, Sequence, TypedDict
from uuid import UUID

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.tools import BaseTool
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

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


def build_employee_graph(tools: Sequence[BaseTool] | None = None):
    """Compile employee graph. Pass tools to enable the ReAct loop."""
    tools = list(tools or [])
    llm = get_chat_model()
    llm_with_tools = llm.bind_tools(tools) if tools else llm

    def agent_node(state: EmployeeAgentState) -> dict:
        messages = [SystemMessage(content=EMPLOYEE_SYSTEM_PROMPT), *state["messages"]]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    graph = StateGraph(EmployeeAgentState)
    graph.add_node("agent", agent_node)
    graph.add_edge(START, "agent")

    if tools:
        graph.add_node("tools", ToolNode(tools))
        graph.add_conditional_edges("agent", tools_condition)
        graph.add_edge("tools", "agent")
    else:
        graph.add_edge("agent", END)

    return graph.compile()
