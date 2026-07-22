from unittest.mock import patch

import pandas as pd
import pytest

from line.command_parser import (
    MAX_COMMAND_TEXT_LENGTH,
    get_stock_symbol_and_market_type,
    get_stock_symbol_from_fixed_command,
    get_tw_futopt_price,
    parse_line_command,
)
from quote.output import format_stock_price_response


class TestGetStockSymbolAndMarketType:
    """Test cases for get_stock_symbol_and_marke_type function"""

    def test_valid_stock_symbol(self):
        """Test parsing valid stock symbols starting with #"""
        assert get_stock_symbol_and_market_type("2884") == ("2884", "TW")
        assert get_stock_symbol_and_market_type("2330") == ("2330", "TW")
        assert get_stock_symbol_and_market_type("1234") == ("1234", "TW")
        assert get_stock_symbol_and_market_type("AAPL") == ("AAPL", "US")
        assert get_stock_symbol_and_market_type("TSLA") == ("TSLA", "US")
        assert get_stock_symbol_and_market_type("aapl") == (
            "AAPL",
            "US",
        )  # Should convert to uppercase

    def test_valid_stock_symbol_with_spaces(self):
        """Test parsing with leading/trailing spaces"""
        assert get_stock_symbol_and_market_type("  2884  ") == ("2884", "TW")
        assert get_stock_symbol_and_market_type("\t2330\n") == ("2330", "TW")
        assert get_stock_symbol_and_market_type("  AAPL  ") == ("AAPL", "US")

    def test_invalid_formats(self):
        """Test various invalid formats"""
        assert get_stock_symbol_and_market_type("#") is None  # Just #
        assert get_stock_symbol_and_market_type("##2884") is None  # Double #
        assert get_stock_symbol_and_market_type("") is None  # Empty string
        assert get_stock_symbol_and_market_type("2884 extra text") == (
            "2884extratext",
            "TW",
        )  # extra space is removed
        assert get_stock_symbol_and_market_type("AAPL extra text") == (
            "AAPLEXTRATEXT",
            "US",
        )  # extra space is removed and symbol is converted to uppercase

    def test_edge_cases(self):
        """Test edge cases"""
        assert get_stock_symbol_and_market_type("0") == ("0", "TW")
        assert get_stock_symbol_and_market_type("123456") == (
            "123456",
            "TW",
        )  # Long number
        assert get_stock_symbol_and_market_type("A") == ("A", "US")  # Single letter
        assert get_stock_symbol_and_market_type("ABC123") == (
            "ABC123",
            "US",
        )  # Mixed alphanumeric

    def test_fixed_commands(self):
        """Test fixed commands like #大盤, #美股, etc."""
        # These should be handled by get_stock_symbol_from_fixed_command internally
        result = get_stock_symbol_and_market_type("大盤")
        assert result == ("IX0001", "TW_IND")

        # Test #美股 returns a list
        result = get_stock_symbol_and_market_type("美股")
        assert isinstance(result, list)
        assert len(result) == 4

    def test_tw_company_name(self):
        """Test tw company commands like #台積電, #長榮, etc."""
        # These should be handled by get_tw_stock_symbol_from_company_name internally
        result = get_stock_symbol_and_market_type("台積電")
        assert result == ("2330", "TW")

        result = get_stock_symbol_and_market_type("長榮")
        assert result == ("2603", "TW")


class TestGetStockSymbolFromFixedCommand:
    """Test cases for get_stock_symbol_from_fixed_command function"""

    def test_dapan_command(self):
        """Test #大盤 command"""
        result = get_stock_symbol_from_fixed_command("大盤")
        assert result == ("IX0001", "TW_IND")

    def test_us_stocks_command(self):
        """Test #美股 command returns list of US indices"""
        result = get_stock_symbol_from_fixed_command("美股")
        assert isinstance(result, list)
        assert len(result) == 4
        assert ("^GSPC", "IND") in result
        assert ("^DJI", "IND") in result
        assert ("^IXIC", "IND") in result
        assert ("^SOX", "IND") in result

    def test_usd_command(self):
        """Test #美元 command"""
        result = get_stock_symbol_from_fixed_command("美元")
        assert result == ("TWD=X", "FUT")

    def test_jpy_command(self):
        """Test #日元 command"""
        result = get_stock_symbol_from_fixed_command("日元")
        assert result == ("JPYTWD=X", "FUT")

    def test_tw_futures_command(self):
        """Test #台指期 command maps to TXFR1 with TW_FUT market type"""
        result = get_stock_symbol_from_fixed_command("台指期")
        assert result == ("TXFR1", "TW_FUT")

    def test_tsmc_futures_command(self):
        """Test #台積期 command maps to CDFR1 with TW_FUT market type"""
        result = get_stock_symbol_from_fixed_command("台積期")
        assert result == ("CDFR1", "TW_FUT")

    def test_unknown_command_fallback(self):
        """Test unknown command should return None"""
        result = get_stock_symbol_from_fixed_command("台積電")
        assert result is None


class TestFormatStockPriceResponse:
    """Test cases for format_stock_price_response function"""

    def test_format_price_up(self):
        """Test formatting when price is up"""
        stock_info = {
            "name": "Apple Inc.",
            "symbol": "AAPL",
            "price": 150.0,
            "previous_price": 140.0,
        }
        result = format_stock_price_response(stock_info)
        assert "Apple Inc." in result
        assert "AAPL" in result
        assert "150.0" in result
        assert "📈" in result
        assert "+10.0" in result or "+7.14" in result  # Price diff and percentage

    def test_format_price_down(self):
        """Test formatting when price is down"""
        stock_info = {
            "name": "Apple Inc.",
            "symbol": "AAPL",
            "price": 140.0,
            "previous_price": 150.0,
        }
        result = format_stock_price_response(stock_info)
        assert "Apple Inc." in result
        assert "AAPL" in result
        assert "140.0" in result
        assert "📉" in result
        assert "-10.0" in result or "-6.67" in result  # Price diff and percentage

    def test_format_price_unchanged(self):
        """Test formatting when price is unchanged"""
        stock_info = {
            "name": "Apple Inc.",
            "symbol": "AAPL",
            "price": 150.0,
            "previous_price": 150.0,
        }
        result = format_stock_price_response(stock_info)
        assert "Apple Inc." in result
        assert "AAPL" in result
        assert "150.0" in result
        assert "➖" in result
        assert "0" in result


class TestParseLineCommand:
    """Test cases for parse_line_command function"""

    @patch("line.command_parser.get_tw_stock_price")
    def test_tw_stock_info(self, mock_get_tw_price):
        """Test getting Taiwan stock info"""
        mock_get_tw_price.return_value = {
            "symbol": "2884",
            "name": "Yuanta Financial",
            "price": 25.5,
            "previous_price": 25.0,
            "currency": "TWD",
        }

        result = parse_line_command("#2884")

        assert result is not None
        assert "2884" in result
        assert "Yuanta Financial" in result
        mock_get_tw_price.assert_called_once_with("2884")

    @patch("line.command_parser.quote_stock")
    def test_us_stock_info(self, mock_quote_stock):
        """Test getting US stock info"""
        mock_quote_stock.return_value = {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "price": 150.0,
            "previous_price": 152.0,
            "currency": "USD",
        }

        result = parse_line_command("#AAPL")

        assert result is not None
        assert "AAPL" in result
        assert "Apple Inc." in result
        mock_quote_stock.assert_called_once_with("AAPL")

    @patch("line.command_parser.generate_groq_technical_analysis_response")
    @patch("line.command_parser.get_tw_stock_price")
    def test_basic_analysis_ignores_trailing_missing_close(self, mock_get_tw_price, mock_generate_analysis):
        """A partial Yahoo row must not make every moving average NaN."""
        mock_get_tw_price.return_value = {
            "symbol": "2891",
            "name": "CTBC Financial",
            "price": 62.7,
            "previous_price": 61.5,
            "currency": "TWD",
            "fullInfo": {"exchange": "TWSE"},
            "history": pd.DataFrame({"Close": [*range(1, 241), float("nan")]}),
        }
        mock_generate_analysis.return_value = "analysis"

        result = parse_line_command("A2891")

        assert "5日線: 238.0  月線: 230.5" in result
        assert "季線: 210.5  半年線: 180.5  年線: 120.5" in result
        assert "線: nan" not in result.lower()
        mock_get_tw_price.assert_called_once_with("2891", period="1y")

    def test_non_stock_command(self):
        """Test non-stock commands return None"""
        assert parse_line_command("Hello world") is None
        assert parse_line_command("2884") is None
        assert parse_line_command("") is None

    def test_command_too_long(self):
        """Test overly long commands are ignored"""
        too_long_command = "#" + ("A" * (MAX_COMMAND_TEXT_LENGTH + 1))
        assert parse_line_command(too_long_command) is None

    @patch("line.command_parser.get_tw_stock_price")
    def test_tw_stock_not_found(self, mock_get_tw_price):
        """Test when Taiwan stock is not found"""
        mock_get_tw_price.return_value = None

        assert parse_line_command("#9999") == ""
        mock_get_tw_price.assert_called_once_with("9999")

    @patch("line.command_parser.quote_stock")
    def test_us_stock_not_found(self, mock_quote_stock):
        """Test when US stock is not found"""
        mock_quote_stock.return_value = None

        assert parse_line_command("#INVALID") == ""
        mock_quote_stock.assert_called_once_with("INVALID")

    @patch("line.command_parser.quote_stock")
    def test_multiple_stocks(self, mock_quote_stock):
        """Test parsing multiple stocks (like #美股)"""
        mock_quote_stock.side_effect = [
            {
                "symbol": "^GSPC",
                "name": "S&P 500",
                "price": 4000.0,
                "previous_price": 3990.0,
                "currency": "USD",
            },
            {
                "symbol": "^DJI",
                "name": "Dow Jones",
                "price": 35000.0,
                "previous_price": 34900.0,
                "currency": "USD",
            },
            {
                "symbol": "^IXIC",
                "name": "NASDAQ",
                "price": 12000.0,
                "previous_price": 11900.0,
                "currency": "USD",
            },
            {
                "symbol": "^SOX",
                "name": "SOX",
                "price": 3000.0,
                "previous_price": 2990.0,
                "currency": "USD",
            },
        ]

        result = parse_line_command("#美股")

        assert result is not None
        assert "S&P 500" in result or "^GSPC" in result
        assert mock_quote_stock.call_count == 4

    @patch("line.command_parser.get_futopt_snapshot")
    def test_tw_futures_index(self, mock_get_futopt_snapshot):
        """Test #台指期 returns Taiwan futures index price."""
        mock_get_futopt_snapshot.return_value = {
            "close": 22000.0,
            "change_price": 200.0,
            "change_rate": 0.92,
            "reference_price": 21800.0,
        }

        result = parse_line_command("#台指期")

        assert result is not None
        assert "台指期" in result
        assert "22000" in result
        assert "📈" in result
        mock_get_futopt_snapshot.assert_called_once_with("TXFR1")

    @patch("line.command_parser.get_futopt_snapshot")
    def test_get_tw_futopt_price_success(self, mock_get_futopt_snapshot):
        """Test get_tw_futopt_price returns formatted dict."""
        mock_get_futopt_snapshot.return_value = {
            "close": 22000.0,
            "change_price": 200.0,
            "change_rate": 0.92,
            "reference_price": 21800.0,
        }

        result = get_tw_futopt_price("TXFR1")

        assert result is not None
        assert result["symbol"] == "TXFR1"
        assert result["name"] == "台指期"
        assert result["price"] == 22000.0
        assert result["previous_price"] == 21800.0

    @patch("line.command_parser.get_futopt_snapshot")
    def test_get_tw_futopt_price_missing_data(self, mock_get_futopt_snapshot):
        """Test get_tw_futopt_price returns None when snapshot fails."""
        mock_get_futopt_snapshot.return_value = None

        result = get_tw_futopt_price("TXFR1")

        assert result is None

    @patch("line.command_parser.get_futopt_snapshot")
    def test_tsmc_futures_price(self, mock_get_futopt_snapshot):
        """Test #台積期 returns TSMC futures price."""
        mock_get_futopt_snapshot.return_value = {
            "close": 850.0,
            "change_price": 5.0,
            "change_rate": 0.59,
            "reference_price": 845.0,
        }

        result = parse_line_command("#台積期")

        assert result is not None
        assert "台積期" in result
        assert "850" in result
        assert "📈" in result
        mock_get_futopt_snapshot.assert_called_once_with("CDFR1")

    @patch("line.command_parser.get_futopt_snapshot")
    def test_get_tw_futopt_price_tsmc(self, mock_get_futopt_snapshot):
        """Test get_tw_futopt_price returns formatted dict for TSMC futures."""
        mock_get_futopt_snapshot.return_value = {
            "close": 850.0,
            "change_price": -10.0,
            "change_rate": -1.17,
            "reference_price": 860.0,
        }

        result = get_tw_futopt_price("CDFR1")

        assert result is not None
        assert result["symbol"] == "CDFR1"
        assert result["name"] == "台積期"
        assert result["price"] == 850.0
        assert result["previous_price"] == 860.0

    @patch("line.command_parser.get_today_ex_dividend_stocks")
    def test_ex_dividend_command(self, mock_get_today_ex_dividend_stocks):
        """Test D除息 returns today's ex-dividend stocks."""
        mock_get_today_ex_dividend_stocks.return_value = (
            [
                {
                    "market": "上市",
                    "symbol": "2330",
                    "name": "台積電",
                    "cashDividend": "4.0",
                }
            ],
            "2026-06-17",
        )

        result = parse_line_command("D除息")

        assert result is not None
        assert "2026-06-17 今日除息股票 (1 檔):" in result
        assert "台積電 (2330) 現金股利: 4" in result
        mock_get_today_ex_dividend_stocks.assert_called_once_with()


if __name__ == "__main__":
    pytest.main([__file__])
