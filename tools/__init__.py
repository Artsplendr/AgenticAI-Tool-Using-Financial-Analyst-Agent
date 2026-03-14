"""Financial analyst agent tools: market data, metrics, news, calculator."""

from tools.market_data import get_market_data
from tools.financial_metrics import get_financial_metrics
from tools.news_search import search_financial_news
from tools.calculator import financial_calculator

__all__ = [
    "get_market_data",
    "get_financial_metrics",
    "search_financial_news",
    "financial_calculator",
]

AGENT_TOOLS = [
    get_market_data,
    get_financial_metrics,
    search_financial_news,
    financial_calculator,
]
