"""News search tool: recent financial news (Tavily)."""

import os
from langchain_core.tools import tool


@tool
def search_financial_news(query: str, max_results: int = 5) -> str:
    """Search for recent financial news, company announcements, and market sentiment.

    Use for: macroeconomic trends, company news, analyst sentiment, sector updates.
    query: search terms (e.g. 'Tesla earnings', 'Bitcoin regulation', 'Nvidia stock').
    max_results: number of articles to return (default 5).
    """
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return "Error: TAVILY_API_KEY not set in environment. Add it to your .env file."

    try:
        from tavily import TavilyClient
    except ImportError:
        return "Error: tavily-python not installed. Run: pip install tavily-python"

    query = (query or "").strip()
    if not query:
        return "Error: query is required."

    try:
        client = TavilyClient(api_key=api_key)
        response = client.search(
            query=query,
            max_results=min(max_results, 10),
            search_depth="advanced",
            include_answer=False,
        )
        results = response.get("results", [])
    except Exception as e:
        return f"Error searching news: {e}"

    if not results:
        return "No recent news found for this query."

    out = []
    for r in results:
        out.append({
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "content": (r.get("content") or "")[:500],
            "score": r.get("score"),
        })
    import json
    return json.dumps(out, default=str)
