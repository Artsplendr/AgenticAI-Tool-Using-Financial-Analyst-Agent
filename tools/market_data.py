"""Market data tool: current price, market cap, volume, history (Yahoo Finance)."""

import json
from langchain_core.tools import tool


@tool
def get_market_data(symbol: str) -> str:
    """Fetch current market data for a stock or crypto ticker.

    Use for: current price, market cap, trading volume, and recent historical data.
    Examples: 'TSLA', 'AAPL', 'BTC-USD', 'ETH-USD'.
    """
    try:
        import yfinance as yf
    except ImportError:
        return "Error: yfinance not installed. Run: pip install yfinance"

    symbol = (symbol or "").strip().upper()
    if not symbol:
        return "Error: symbol is required (e.g. TSLA, AAPL, BTC-USD)."

    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period="1mo")
    except Exception as e:
        return f"Error fetching data for {symbol}: {e}"

    result = {
        "symbol": symbol,
        "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
        "currency": info.get("currency", "USD"),
        "market_cap": info.get("marketCap"),
        "volume": info.get("volume"),
        "previous_close": info.get("previousClose"),
        "day_high": info.get("dayHigh"),
        "day_low": info.get("dayLow"),
        "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
        "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
    }
    result = {k: v for k, v in result.items() if v is not None}

    if not hist.empty:
        result["last_30d"] = {
            "open": float(hist["Open"].iloc[0]) if len(hist) else None,
            "close": float(hist["Close"].iloc[-1]),
            "high": float(hist["High"].max()),
            "low": float(hist["Low"].min()),
        }

    return json.dumps(result, default=str)
