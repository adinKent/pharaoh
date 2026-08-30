from collections.abc import Callable
from datetime import UTC, datetime

from routing.models import EntityReference
from routing.tool_results import ToolResult


def _now() -> str:
    return datetime.now(UTC).isoformat()


def market_data(entity: EntityReference) -> ToolResult[dict]:
    from quote.tw_stock import get_tw_index_price, get_tw_stock_price
    from quote.yahoo_finance import quote_stock

    try:
        if entity.market == "TW":
            data = get_tw_index_price(entity.symbol) if entity.kind.value == "index" else get_tw_stock_price(entity.symbol)
        else:
            data = quote_stock(entity.symbol)
        if not data:
            return ToolResult(source="market_data", retrieved_at=_now(), quality="unavailable", error="No market data returned")
        return ToolResult(data=data, source="market_data", retrieved_at=_now(), effective_at=data.get("timestamp"), quality="complete")
    except Exception as error:
        return ToolResult(source="market_data", retrieved_at=_now(), quality="unavailable", error=str(error))


def financial_search(entity: EntityReference, *, query: str | None = None) -> ToolResult[str]:
    from utils.web_search import search_stock_by_market, web_search

    try:
        data = (
            web_search(query) if query else search_stock_by_market(entity.symbol or entity.display_name, entity.market or "US", entity.display_name)
        )
        if not data:
            return ToolResult(source="financial_search", retrieved_at=_now(), quality="unavailable", error="No search result returned")
        return ToolResult(data=data, source="financial_search", retrieved_at=_now(), quality="partial")
    except Exception as error:
        return ToolResult(source="financial_search", retrieved_at=_now(), quality="unavailable", error=str(error))


def financial_statements(entity: EntityReference) -> ToolResult[str]:
    result = financial_search(entity, query=f"{entity.display_name} {entity.symbol or ''} financial statements filings")
    result.source = "financial_statements_search"
    return result


def financial_news(entity: EntityReference) -> ToolResult[str]:
    result = financial_search(entity, query=f"{entity.display_name} {entity.symbol or ''} latest financial news")
    result.source = "financial_news_search"
    return result


def bond_data(entity: EntityReference) -> ToolResult[str]:
    result = financial_search(entity, query=f"{entity.display_name} {entity.symbol or ''} bond terms coupon maturity yield")
    result.source = "bond_data_search"
    return result


def portfolio_calculator(weights: dict[str, float]) -> ToolResult[dict[str, float]]:
    total = sum(weights.values())
    if total <= 0:
        return ToolResult(source="portfolio_calculator", retrieved_at=_now(), quality="invalid", error="Portfolio weights must total more than zero")
    normalized = {key: value / total for key, value in weights.items()}
    return ToolResult(data=normalized, source="portfolio_calculator", retrieved_at=_now(), quality="complete")


def knowledge_lookup(query: str) -> ToolResult[str]:
    if not query.strip():
        return ToolResult(source="knowledge", retrieved_at=_now(), quality="invalid", error="Knowledge query is empty")
    return ToolResult(data="", source="knowledge", retrieved_at=_now(), quality="unavailable", error="No knowledge base configured")


TOOL_REGISTRY: dict[str, Callable] = {
    "market_data": market_data,
    "financial_search": financial_search,
    "financial_statements": financial_statements,
    "financial_news": financial_news,
    "bond_data": bond_data,
    "portfolio_calculator": portfolio_calculator,
    "knowledge": knowledge_lookup,
}
