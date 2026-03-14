"""Financial metrics tool: P/E, revenue growth, earnings, margins (Yahoo Finance)."""

import json
from langchain_core.tools import tool


@tool
def get_financial_metrics(symbol: str) -> str:
    """Get key financial indicators for a stock: P/E ratio, revenue growth, earnings, profit margins.

    Use for stocks only (e.g. TSLA, AAPL). Not for crypto.
    """
    try:
        import yfinance as yf
    except ImportError:
        return "Error: yfinance not installed. Run: pip install yfinance"

    symbol = (symbol or "").strip().upper()
    if not symbol:
        return "Error: symbol is required (e.g. TSLA, AAPL)."

    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
    except Exception as e:
        return f"Error fetching metrics for {symbol}: {e}"

    result = {
        "symbol": symbol,
        "trailing_pe": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "peg_ratio": info.get("pegRatio"),
        "profit_margins": info.get("profitMargins"),
        "operating_margins": info.get("operatingMargins"),
        "revenue_growth": info.get("revenueGrowth"),
        "earnings_growth": info.get("earningsGrowth"),
        "earnings_quarterly_growth": info.get("earningsQuarterlyGrowth"),
        "return_on_equity": info.get("returnOnEquity"),
        "return_on_assets": info.get("returnOnAssets"),
        "debt_to_equity": info.get("debtToEquity"),
        "current_ratio": info.get("currentRatio"),
        "quick_ratio": info.get("quickRatio"),
        "free_cash_flow": info.get("freeCashflow"),
        "operating_cash_flow": info.get("operatingCashflow"),
        "revenue": info.get("totalRevenue"),
        "earnings": info.get("earnings"),
        "ebitda": info.get("ebitda"),
    }
    result = {k: v for k, v in result.items() if v is not None}

    return json.dumps(result, default=str) if result else json.dumps({"symbol": symbol, "message": "No financial metrics available for this ticker."})
