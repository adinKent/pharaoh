from unittest.mock import MagicMock, patch

import pandas as pd

from quote.dividend import (
    aggregate_dividend_records,
    fetch_dividends_yfinance,
    fetch_stock_header_info,
    fetch_tw_stock_dividends_finmind,
    generate_dividend_chart_png,
)


class TestAggregateDividendRecords:
    def test_aggregates_past_years_and_keeps_current_year_individual(self):
        current_year = 2026
        start_year = 2021
        records = [
            # Past year 2022
            {"date": "2022-03-16", "cash": 2.75, "stock": 0.0},
            {"date": "2022-06-16", "cash": 2.75, "stock": 0.0},
            {"date": "2022-09-15", "cash": 2.75, "stock": 0.0},
            {"date": "2022-12-15", "cash": 2.75, "stock": 0.0},
            # Past year 2023 with stock dividend
            {"date": "2023-07-20", "cash": 3.0, "stock": 1.0},
            # Current year 2026: 2 payouts
            {"date": "2026-03-18", "cash": 3.5, "stock": 0.0},
            {"date": "2026-06-12", "cash": 4.0, "stock": 0.5},
            # Out of bounds older record
            {"date": "2019-05-10", "cash": 2.0, "stock": 0.0},
        ]

        result = aggregate_dividend_records(records, current_year, start_year)

        assert len(result) == 4
        # 2022 sum: 2.75 * 4 = 11.0
        assert result[0] == {"label": "2022", "cash": 11.0, "stock": 0.0, "is_current_year": False}
        # 2023 sum: cash=3.0, stock=1.0
        assert result[1] == {"label": "2023", "cash": 3.0, "stock": 1.0, "is_current_year": False}
        # 2026 Q1
        assert result[2] == {"label": "03/18", "cash": 3.5, "stock": 0.0, "is_current_year": True}
        # 2026 Q2
        assert result[3] == {"label": "06/12", "cash": 4.0, "stock": 0.5, "is_current_year": True}

    def test_empty_records(self):
        assert aggregate_dividend_records([], 2026, 2021) == []
        assert aggregate_dividend_records([{"date": "2010-01-01", "cash": 1.0, "stock": 0.0}], 2026, 2021) == []


class TestFetchTwStockDividendsFinmind:
    @patch("quote.dividend.requests.get")
    def test_success(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "data": [
                {
                    "date": "2024-06-13",
                    "CashEarningsDistribution": 3.5,
                    "CashStatutorySurplus": 0.0,
                    "StockEarningsDistribution": 0.0,
                    "StockStatutorySurplus": 0.0,
                },
                {
                    "date": "2024-09-12",
                    "CashEarningsDistribution": 4.0,
                    "CashStatutorySurplus": 0.5,
                    "StockEarningsDistribution": 1.0,
                    "StockStatutorySurplus": 0.0,
                },
            ]
        }
        mock_get.return_value = mock_resp

        records = fetch_tw_stock_dividends_finmind("2330", 2021)
        assert len(records) == 2
        assert records[0] == {"date": "2024-06-13", "cash": 3.5, "stock": 0.0}
        assert records[1] == {"date": "2024-09-12", "cash": 4.5, "stock": 1.0}

    @patch("quote.dividend.requests.get")
    def test_failure(self, mock_get):
        mock_get.side_effect = Exception("Network timeout")
        records = fetch_tw_stock_dividends_finmind("2330", 2021)
        assert records == []


class TestFetchDividendsYfinance:
    @patch("quote.dividend.yf.Ticker")
    def test_us_stock_dividends(self, mock_ticker_cls):
        mock_ticker = MagicMock()
        idx = pd.to_datetime(["2023-02-10", "2023-05-12", "2023-08-11", "2023-11-10"])
        mock_ticker.dividends = pd.Series([0.23, 0.24, 0.24, 0.24], index=idx)
        mock_ticker_cls.return_value = mock_ticker

        records = fetch_dividends_yfinance("AAPL", "US", 2021)
        assert len(records) == 4
        assert records[0] == {"date": "2023-02-10", "cash": 0.23, "stock": 0.0}


class TestFetchStockHeaderInfo:
    @patch("quote.dividend.get_tw_stock_price")
    def test_tw_stock_header_info(self, mock_get_price):
        mock_get_price.return_value = {
            "name": "台積電",
            "price": 1000.0,
            "previous_price": 990.0,
        }
        # TTM records (all within last 365 days from 2026-09)
        records = [
            {"date": "2026-06-15", "cash": 4.0, "stock": 0.0},
            {"date": "2026-03-18", "cash": 4.0, "stock": 0.0},
            {"date": "2025-12-15", "cash": 3.5, "stock": 0.0},
            {"date": "2025-09-15", "cash": 3.5, "stock": 0.0},
        ]
        info = fetch_stock_header_info("2330", "TW", records)
        assert info["symbol"] == "2330"
        assert info["name"] == "台積電"
        assert info["price"] == 1000.0
        assert info["ttm_cash"] == 15.0
        assert info["yield_pct"] == 1.5  # 15 / 1000 * 100


class TestGenerateDividendChartPng:
    @patch("quote.dividend.save_or_upload_fig")
    @patch("quote.dividend.fetch_stock_header_info")
    @patch("quote.dividend.fetch_tw_stock_dividends_finmind")
    def test_generates_chart_successfully(self, mock_fetch_finmind, mock_header, mock_save):
        mock_fetch_finmind.return_value = [
            {"date": "2023-06-15", "cash": 10.0, "stock": 1.0},
            {"date": "2024-06-15", "cash": 12.0, "stock": 0.0},
        ]
        mock_header.return_value = {
            "symbol": "2330",
            "name": "台積電",
            "price": 1000.0,
            "yield_pct": 1.2,
            "ttm_cash": 12.0,
        }
        mock_save.return_value = "https://s3.amazonaws.com/test-bucket/2330_dividend_123.jpg"

        result = generate_dividend_chart_png("2330", "TW", save_to_local_file=False)
        assert result == "https://s3.amazonaws.com/test-bucket/2330_dividend_123.jpg"
        mock_save.assert_called_once()

    @patch("quote.dividend.fetch_tw_stock_dividends_finmind")
    @patch("quote.dividend.fetch_dividends_yfinance")
    def test_returns_none_when_no_records(self, mock_yf, mock_finmind):
        mock_finmind.return_value = []
        mock_yf.return_value = []
        result = generate_dividend_chart_png("2330", "TW", save_to_local_file=False)
        assert result is None
