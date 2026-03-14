"""
LangGraph agentic workflow: Financial Analyst Agent.

Flow: User Query -> Agent (LLM + tools) -> [Tool calls] -> Tools node -> Agent -> ... -> Report.
"""

import os
from typing import Annotated, Literal

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from tools import AGENT_TOOLS


class AgentState(TypedDict):
    """Graph state: messages list with add_messages reducer."""

    messages: Annotated[list, add_messages]


def _get_llm():
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    return ChatOpenAI(model=model, temperature=0)


SYSTEM_PROMPT = """You are a financial analyst agent. Your job is to analyze stocks or cryptocurrencies based on user requests.

Use the tools available to you to gather:
- Current market data (price, market cap, volume) via get_market_data
- Financial metrics (P/E, margins, growth) via get_financial_metrics for stocks
- Recent news and sentiment via search_financial_news
- Numeric calculations (percent change, ratios) via financial_calculator when needed

After gathering data, produce a structured report using exactly these markdown section headers (##) so the UI can display them in columns:
## Asset/Summary
(asset name, ticker, current price, brief summary)
## Key Metrics
(market cap, P/E, revenue growth, margins, etc.)
## Recent News
(bullet points or short paragraphs)
## Opportunities
(bullet points)
## Risks
(bullet points)

Use each header exactly as written above. Be concise and factual. If data is missing for a ticker, say so."""


def _agent_node(state: AgentState) -> dict:
    """Call LLM with tools; returns new messages (possibly with tool_calls)."""
    llm = _get_llm().bind_tools(AGENT_TOOLS)
    messages = state["messages"]
    # Prepend system message if not already present
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)
    response = llm.invoke(messages)
    return {"messages": [response]}


def _tools_node(state: AgentState) -> dict:
    """Execute tool calls from the last AI message and return ToolMessages."""
    last = state["messages"][-1]
    if not isinstance(last, AIMessage) or not last.tool_calls:
        return {"messages": []}
    tool_messages = []
    by_name = {t.name: t for t in AGENT_TOOLS}
    for tc in last.tool_calls:
        name = tc["name"]
        args = tc.get("args") or {}
        tool = by_name.get(name)
        if not tool:
            tool_messages.append(
                ToolMessage(content=f"Unknown tool: {name}", tool_call_id=tc["id"])
            )
            continue
        try:
            result = tool.invoke(args)
            tool_messages.append(
                ToolMessage(content=str(result), tool_call_id=tc["id"])
            )
        except Exception as e:
            tool_messages.append(
                ToolMessage(content=f"Error: {e}", tool_call_id=tc["id"])
            )
    return {"messages": tool_messages}


def _route_after_agent(state: AgentState):
    """If the last message has tool_calls, go to tools; else end."""
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    return END


def create_financial_agent():
    """Build and compile the LangGraph financial analyst agent (ReAct-style with tools)."""
    builder = StateGraph(AgentState)
    builder.add_node("agent", _agent_node)
    builder.add_node("tools", _tools_node)
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", _route_after_agent)
    builder.add_edge("tools", "agent")
    return builder.compile()


def run_analysis(user_query: str, agent=None) -> str:
    """
    Run the financial analysis agent on a user query and return the final report text.

    Args:
        user_query: Natural language request (e.g. "Analyze Tesla stock and summarize risks").
        agent: Optional pre-built agent; if None, one is created.

    Returns:
        The last AI message content (structured financial report).
    """
    if agent is None:
        agent = create_financial_agent()

    config = {"recursion_limit": 50}
    result = agent.invoke(
        {"messages": [HumanMessage(content=user_query)]},
        config=config,
    )
    messages = result.get("messages", [])
    if not messages:
        return "No response generated."
    last = messages[-1]
    if isinstance(last, AIMessage) and last.content:
        return last.content
    for m in reversed(messages):
        if isinstance(m, AIMessage) and m.content:
            return m.content
    return "No analysis text in response."