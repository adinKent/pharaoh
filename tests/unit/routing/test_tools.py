from unittest.mock import patch

from routing.models import EntityKind, EntityReference
from routing.tool_results import ToolResult
from routing.tools import TOOL_REGISTRY, financial_news, market_data, portfolio_calculator

ENTITY = EntityReference(
    kind=EntityKind.SECURITY,
    canonical_id="US:AAPL",
    symbol="AAPL",
    market="US",
    display_name="Apple",
    confidence=1,
)


def test_tool_registry_contains_all_planner_tools():
    assert {
        "market_data",
        "financial_search",
        "financial_statements",
        "financial_news",
        "bond_data",
        "portfolio_calculator",
    } <= set(TOOL_REGISTRY)


@patch("quote.yahoo_finance.quote_stock", return_value={"symbol": "AAPL", "price": 100, "timestamp": "2026-08-30T12:00:00Z"})
def test_market_adapter_returns_shared_result(mock_quote):
    result = market_data(ENTITY)

    assert isinstance(result, ToolResult)
    assert result.source == "market_data"
    assert result.effective_at == "2026-08-30T12:00:00Z"
    mock_quote.assert_called_once_with("AAPL")


@patch("utils.web_search.web_search", return_value="latest news")
def test_news_adapter_returns_provenance(mock_search):
    result = financial_news(ENTITY)

    assert result.source == "financial_news_search"
    assert result.data == "latest news"
    mock_search.assert_called_once()


def test_portfolio_calculator_normalizes_weights():
    result = portfolio_calculator({"A": 20, "B": 30})

    assert result.data == {"A": 0.4, "B": 0.6}
