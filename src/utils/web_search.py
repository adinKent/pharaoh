import logging
import re
from html import unescape

import requests
import yfinance as yf

logger = logging.getLogger(__name__)

_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
_TIMEOUT_SECONDS = 8
_MAX_TEXT_CHARS = 3500

# Yahoo Finance HTML subpages (/key-statistics, /profile, /analysis) return 404 to
# non-browser clients; use yfinance quoteSummary fields instead.
_US_INFO_FIELDS = (
    ("longName", "Name"),
    ("sector", "Sector"),
    ("industry", "Industry"),
    ("marketCap", "Market Cap"),
    ("enterpriseValue", "Enterprise Value"),
    ("trailingPE", "Trailing PE"),
    ("forwardPE", "Forward PE"),
    ("pegRatio", "PEG"),
    ("priceToBook", "P/B"),
    ("priceToSalesTrailing12Months", "P/S"),
    ("profitMargins", "Profit Margin"),
    ("operatingMargins", "Operating Margin"),
    ("returnOnEquity", "ROE"),
    ("returnOnAssets", "ROA"),
    ("revenueGrowth", "Revenue Growth"),
    ("earningsGrowth", "Earnings Growth"),
    ("earningsQuarterlyGrowth", "Earnings QoQ Growth"),
    ("dividendYield", "Dividend Yield"),
    ("dividendRate", "Dividend Rate"),
    ("payoutRatio", "Payout Ratio"),
    ("exDividendDate", "Ex-Dividend Date"),
    ("fiftyTwoWeekHigh", "52W High"),
    ("fiftyTwoWeekLow", "52W Low"),
    ("fiftyDayAverage", "50D MA"),
    ("twoHundredDayAverage", "200D MA"),
    ("averageVolume", "Avg Volume"),
    ("beta", "Beta"),
    ("targetMeanPrice", "Target Mean"),
    ("recommendationKey", "Recommendation"),
    ("numberOfAnalystOpinions", "Analysts"),
    ("totalCash", "Total Cash"),
    ("totalDebt", "Total Debt"),
    ("freeCashflow", "Free Cash Flow"),
    ("longBusinessSummary", "Summary"),
)


def _strip_html(html: str) -> str:
    text = re.sub(r"(?is)<(script|style|noscript).*?>.*?</\1>", " ", html)
    text = re.sub(r"(?is)<br\s*/?>", "\n", text)
    text = re.sub(r"(?is)</p>", "\n", text)
    text = re.sub(r"(?is)<[^>]+>", " ", text)
    text = unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _fetch_text(url: str) -> str:
    response = requests.get(
        url,
        timeout=_TIMEOUT_SECONDS,
        headers={"User-Agent": _USER_AGENT, "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8"},
    )
    response.raise_for_status()
    return _strip_html(response.text)[:_MAX_TEXT_CHARS]


def _duckduckgo_instant_answer(query: str) -> str:
    response = requests.get(
        "https://api.duckduckgo.com/",
        params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
        timeout=_TIMEOUT_SECONDS,
        headers={"User-Agent": _USER_AGENT},
    )
    response.raise_for_status()
    data = response.json()
    parts: list[str] = []
    abstract = (data.get("AbstractText") or "").strip()
    if abstract:
        source = (data.get("AbstractURL") or "").strip()
        parts.append(f"{abstract}" + (f" ({source})" if source else ""))
    for topic in data.get("RelatedTopics") or []:
        if isinstance(topic, dict) and topic.get("Text"):
            parts.append(topic["Text"].strip())
        if len(parts) >= 5:
            break
    return "\n".join(parts)[:_MAX_TEXT_CHARS]


def web_search(query: str) -> str:
    """General web search via DuckDuckGo instant answer API."""
    query = (query or "").strip()
    if not query:
        return ""
    try:
        result = _duckduckgo_instant_answer(query)
        return result or f"No instant answer for: {query}"
    except Exception:
        logger.exception("web_search failed for query=%s", query)
        return ""


def search_tw_stock(symbol: str, name: str | None = None) -> str:
    """Fetch latest TW stock fundamentals from Yahoo TW pages + web search."""
    symbol = (symbol or "").strip().upper()
    if not symbol:
        return ""

    exchange_suffixes = ("TW", "TWO")
    chunks: list[str] = []
    label = name or symbol

    for suffix in exchange_suffixes:
        yahoo_symbol = f"{symbol}.{suffix}"
        for path, title in (("profile", "公司資料"), ("dividend", "股利")):
            url = f"https://tw.stock.yahoo.com/quote/{yahoo_symbol}/{path}"
            try:
                text = _fetch_text(url)
                if text and len(text) > 80:
                    chunks.append(f"[{title} {yahoo_symbol}]\n{text}")
            except Exception:
                logger.exception("TW yahoo fetch failed url=%s", url)

        if chunks:
            break

    try:
        search_hit = web_search(f"{label} {symbol} 台股 基本面 財報 股利")
        if search_hit:
            chunks.append(f"[網路搜尋]\n{search_hit}")
    except Exception:
        logger.exception("TW web_search failed symbol=%s", symbol)

    return "\n\n".join(chunks)[: _MAX_TEXT_CHARS * 2]


def _format_us_info_value(key: str, value) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        if key in {
            "profitMargins",
            "operatingMargins",
            "returnOnEquity",
            "returnOnAssets",
            "revenueGrowth",
            "earningsGrowth",
            "earningsQuarterlyGrowth",
            "dividendYield",
            "payoutRatio",
        }:
            return f"{value * 100:.2f}%"
        if abs(value) >= 1e9:
            return f"{value / 1e9:.2f}B"
        if abs(value) >= 1e6:
            return f"{value / 1e6:.2f}M"
        return f"{value:.2f}"
    if isinstance(value, int) and key in {"marketCap", "enterpriseValue", "totalCash", "totalDebt", "freeCashflow", "averageVolume"}:
        if abs(value) >= 1e9:
            return f"{value / 1e9:.2f}B"
        if abs(value) >= 1e6:
            return f"{value / 1e6:.2f}M"
        return f"{value:,}"
    text = str(value).strip()
    if key == "longBusinessSummary" and len(text) > 600:
        return text[:600] + "..."
    return text


def _us_fundamentals_from_yfinance(symbol: str) -> str:
    info = yf.Ticker(symbol).info or {}
    if not info:
        return ""
    lines: list[str] = []
    for key, label in _US_INFO_FIELDS:
        formatted = _format_us_info_value(key, info.get(key))
        if formatted:
            lines.append(f"{label}: {formatted}")
    return "\n".join(lines)


def search_us_stock(symbol: str, name: str | None = None) -> str:
    """Fetch latest US stock fundamentals via yfinance + web search.

    Do not scrape finance.yahoo.com HTML subpages — they 404 for non-browser clients.
    """
    symbol = (symbol or "").strip().upper()
    if not symbol:
        return ""

    chunks: list[str] = []
    label = name or symbol

    try:
        fundamentals = _us_fundamentals_from_yfinance(symbol)
        if fundamentals:
            chunks.append(f"[Fundamentals {symbol}]\n{fundamentals}")
    except Exception:
        logger.exception("US yfinance fundamentals failed symbol=%s", symbol)

    try:
        search_hit = web_search(f"{label} {symbol} stock fundamentals earnings dividend PE")
        if search_hit:
            chunks.append(f"[Web search]\n{search_hit}")
    except Exception:
        logger.exception("US web_search failed symbol=%s", symbol)

    return "\n\n".join(chunks)[: _MAX_TEXT_CHARS * 2]


def search_stock_by_market(symbol: str, market_type: str, name: str | None = None) -> str:
    """Route search by market type (TW / TW_IND / US / other)."""
    market = (market_type or "").upper()
    if market in {"TW", "TW_IND"}:
        return search_tw_stock(symbol, name=name)
    return search_us_stock(symbol, name=name)
