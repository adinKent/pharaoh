from unittest.mock import Mock

import pytest

from utils import web_search as ws


def test_web_search_empty_query():
    assert ws.web_search("") == ""
    assert ws.web_search("   ") == ""


def test_web_search_uses_duckduckgo(mocker):
    response = Mock()
    response.raise_for_status = Mock()
    response.json.return_value = {
        "AbstractText": "Apple designs consumer electronics.",
        "AbstractURL": "https://example.com",
        "RelatedTopics": [{"Text": "iPhone is a product line."}],
    }
    get = mocker.patch.object(ws.requests, "get", return_value=response)

    result = ws.web_search("AAPL stock")

    assert "Apple designs consumer electronics" in result
    assert "iPhone is a product line" in result
    assert get.call_args.kwargs["params"]["q"] == "AAPL stock"


def test_web_search_failure_returns_empty(mocker):
    mocker.patch.object(ws.requests, "get", side_effect=RuntimeError("network"))
    mocker.patch.object(ws.logger, "exception")
    assert ws.web_search("AAPL") == ""


def test_search_tw_stock_fetches_yahoo_and_search(mocker):
    html = "<html><body><p>" + ("台積電 基本資料 " * 20) + "</p></body></html>"
    page = Mock()
    page.raise_for_status = Mock()
    page.text = html

    ddg = Mock()
    ddg.raise_for_status = Mock()
    ddg.json.return_value = {"AbstractText": "TSMC news", "AbstractURL": "", "RelatedTopics": []}

    def fake_get(url, **kwargs):
        if "duckduckgo" in url or url.endswith("/"):
            return ddg
        return page

    mocker.patch.object(ws.requests, "get", side_effect=fake_get)

    result = ws.search_tw_stock("2330", name="台積電")

    assert "公司資料" in result or "股利" in result
    assert "2330" in result
    assert "TSMC news" in result or "網路搜尋" in result


def test_search_us_stock_uses_yfinance_and_search(mocker):
    ticker = Mock()
    ticker.info = {
        "longName": "Apple Inc.",
        "sector": "Technology",
        "trailingPE": 28.5,
        "dividendYield": 0.005,
        "marketCap": 3_000_000_000_000,
        "longBusinessSummary": "Apple designs consumer electronics.",
    }
    mocker.patch.object(ws.yf, "Ticker", return_value=ticker)
    mocker.patch.object(ws, "web_search", return_value="Apple earnings beat")

    result = ws.search_us_stock("AAPL", name="Apple")

    assert "AAPL" in result
    assert "Apple Inc." in result
    assert "Trailing PE: 28.50" in result
    assert "Dividend Yield: 0.50%" in result
    assert "Apple earnings beat" in result
    ws.yf.Ticker.assert_called_once_with("AAPL")


@pytest.mark.parametrize(
    ("market_type", "expected_fn"),
    [
        ("TW", "search_tw_stock"),
        ("TW_IND", "search_tw_stock"),
        ("US", "search_us_stock"),
        ("OTHER", "search_us_stock"),
    ],
)
def test_search_stock_by_market_routes(mocker, market_type, expected_fn):
    tw = mocker.patch.object(ws, "search_tw_stock", return_value="tw")
    us = mocker.patch.object(ws, "search_us_stock", return_value="us")

    result = ws.search_stock_by_market("X", market_type, name="N")

    if expected_fn == "search_tw_stock":
        tw.assert_called_once_with("X", name="N")
        us.assert_not_called()
        assert result == "tw"
    else:
        us.assert_called_once_with("X", name="N")
        tw.assert_not_called()
        assert result == "us"
