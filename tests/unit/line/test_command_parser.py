from unittest.mock import patch
import pytest

from line.command_parser import (
    get_stock_symbol_and_market_type,
    parse_line_command,
    get_stock_symbol_from_fixed_command,
    format_stock_price_response
)


class TestGetStockSymbolAndMarketType:
    """Test cases for get_stock_symbol_and_marke_type function"""

    def test_valid_stock_symbol(self):
        """Test parsing valid stock symbols starting with #"""
        assert get_stock_symbol_and_market_type("2884") == ("2884", "TW")
        assert get_stock_symbol_and_market_type("2330") == ("2330", "TW")
        assert get_stock_symbol_and_market_type("1234") == ("1234", "TW")
        assert get_stock_symbol_and_market_type("AAPL") == ("AAPL", "US")
        assert get_stock_symbol_and_market_type("TSLA") == ("TSLA", "US")
        assert get_stock_symbol_and_market_type("aapl") == ("AAPL", "US")  # Should convert to uppercase

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
        assert get_stock_symbol_and_market_type("2884 extra text") == ("2884extratext", "TW")  # extra space is removed
        assert get_stock_symbol_and_market_type("AAPL extra text") == ("AAPLEXTRATEXT", "US")  # extra space is removed and symbol is converted to uppercase

    def test_edge_cases(self):
        """Test edge cases"""
        assert get_stock_symbol_and_market_type("0") == ("0", "TW")
        assert get_stock_symbol_and_market_type("123456") == ("123456", "TW")  # Long number
        assert get_stock_symbol_and_market_type("A") == ("A", "US")  # Single letter
        assert get_stock_symbol_and_market_type("ABC123") == ("ABC123", "US")  # Mixed alphanumeric

    def test_fixed_commands(self):
        """Test fixed commands like #大盤, #美股, etc."""
        # These should be handled by get_stock_symbol_from_fixed_command internally
        result = get_stock_symbol_and_market_type("大盤")
        assert result == ("^TWII", "IND")

        # Test #美股 returns a list
        result = get_stock_symbol_and_market_type("美股")
        assert isinstance(result, list)
        assert len(result) == 4


class TestGetStockSymbolFromFixedCommand:
    """Test cases for get_stock_symbol_from_fixed_command function"""

    def test_dapan_command(self):
        """Test #大盤 command"""
        result = get_stock_symbol_from_fixed_command("大盤")
        assert result == ("^TWII", "IND")

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

    @patch('line.command_parser.get_tw_stock_symbol_from_company_name')
    def test_unknown_command_fallback(self, mock_get_symbol):
        """Test unknown command falls back to company name lookup"""
        mock_get_symbol.return_value = "2330"
        result = get_stock_symbol_from_fixed_command("台積電")
        assert result == ("2330", "TW")
        mock_get_symbol.assert_called_once_with("台積電")


class TestFormatStockPriceResponse:
    """Test cases for format_stock_price_response function"""

    def test_format_price_up(self):
        """Test formatting when price is up"""
        stock_info = {
            'name': 'Apple Inc.',
            'symbol': 'AAPL',
            'price': 150.0,
            'previous_price': 140.0
        }
        result = format_stock_price_response(stock_info)
        assert 'Apple Inc.' in result
        assert 'AAPL' in result
        assert '150.0' in result
        assert '📈' in result
        assert '+10.0' in result or '+7.14' in result  # Price diff and percentage

    def test_format_price_down(self):
        """Test formatting when price is down"""
        stock_info = {
            'name': 'Apple Inc.',
            'symbol': 'AAPL',
            'price': 140.0,
            'previous_price': 150.0
        }
        result = format_stock_price_response(stock_info)
        assert 'Apple Inc.' in result
        assert 'AAPL' in result
        assert '140.0' in result
        assert '📉' in result
        assert '-10.0' in result or '-6.67' in result  # Price diff and percentage

    def test_format_price_unchanged(self):
        """Test formatting when price is unchanged"""
        stock_info = {
            'name': 'Apple Inc.',
            'symbol': 'AAPL',
            'price': 150.0,
            'previous_price': 150.0
        }
        result = format_stock_price_response(stock_info)
        assert 'Apple Inc.' in result
        assert 'AAPL' in result
        assert '150.0' in result
        assert '➖' in result
        assert '0' in result


class TestParseLineCommand:
    """Test cases for parse_line_command function"""

    @patch('line.command_parser.get_tw_stock_price')
    def test_tw_stock_info(self, mock_get_tw_price):
        """Test getting Taiwan stock info"""
        mock_get_tw_price.return_value = {
            'symbol': '2884',
            'name': 'Yuanta Financial',
            'price': 25.5,
            'previous_price': 25.0,
            'currency': 'TWD'
        }

        result = parse_line_command("#2884")

        assert result is not None
        assert '2884' in result
        assert 'Yuanta Financial' in result
        mock_get_tw_price.assert_called_once_with("2884")

    @patch('line.command_parser.get_us_stock_price')
    def test_us_stock_info(self, mock_get_us_price):
        """Test getting US stock info"""
        mock_get_us_price.return_value = {
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'price': 150.0,
            'previous_price': 152.0,
            'currency': 'USD'
        }

        result = parse_line_command("#AAPL")

        assert result is not None
        assert 'AAPL' in result
        assert 'Apple Inc.' in result
        mock_get_us_price.assert_called_once_with("AAPL")

    def test_non_stock_command(self):
        """Test non-stock commands return None"""
        assert parse_line_command("Hello world") is None
        assert parse_line_command("2884") is None
        assert parse_line_command("") is None

    @patch('line.command_parser.get_tw_stock_price')
    def test_tw_stock_not_found(self, mock_get_tw_price):
        """Test when Taiwan stock is not found"""
        mock_get_tw_price.return_value = None

        assert parse_line_command("#9999") == ""
        mock_get_tw_price.assert_called_once_with("9999")

    @patch('line.command_parser.get_us_stock_price')
    def test_us_stock_not_found(self, mock_get_us_price):
        """Test when US stock is not found"""
        mock_get_us_price.return_value = None

        assert parse_line_command("#INVALID") == ""
        mock_get_us_price.assert_called_once_with("INVALID")

    @patch('line.command_parser.get_index_price')
    def test_multiple_stocks(self, get_index_price):
        """Test parsing multiple stocks (like #美股)"""
        get_index_price.side_effect = [
            {'symbol': '^GSPC', 'name': 'S&P 500', 'price': 4000.0, 'previous_price': 3990.0, 'currency': 'USD'},
            {'symbol': '^DJI', 'name': 'Dow Jones', 'price': 35000.0, 'previous_price': 34900.0, 'currency': 'USD'},
            {'symbol': '^IXIC', 'name': 'NASDAQ', 'price': 12000.0, 'previous_price': 11900.0, 'currency': 'USD'},
            {'symbol': '^SOX', 'name': 'SOX', 'price': 3000.0, 'previous_price': 2990.0, 'currency': 'USD'}
        ]

        result = parse_line_command("#美股")

        assert result is not None
        assert 'S&P 500' in result or '^GSPC' in result
        assert get_index_price.call_count == 4


if __name__ == "__main__":
    pytest.main([__file__])
