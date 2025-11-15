import pytest
from unittest.mock import patch, Mock
import sys
import os

# Add project root to path so we can import from src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.line.command import get_stock_symbol_from_command, parse_line_command
from src.quote.tw_stock import get_tw_stock_price, _fallback_stock_price
from src.quote.us_stock import get_us_stock_price

# Mock yfinance at module level
sys.modules['yfinance'] = Mock()


class TestParseStockCommand:
    """Test cases for get_stock_symbol_from_command function"""
    
    def test_valid_stock_symbol(self):
        """Test parsing valid stock symbols starting with #"""
        assert get_stock_symbol_from_command("#2884") == ("2884", "TW")
        assert get_stock_symbol_from_command("#2330") == ("2330", "TW")
        assert get_stock_symbol_from_command("#1234") == ("1234", "TW")
        assert get_stock_symbol_from_command("#AAPL") == ("AAPL", "US")
        assert get_stock_symbol_from_command("#TSLA") == ("TSLA", "US")
        assert get_stock_symbol_from_command("#aapl") == ("AAPL", "US")  # Should convert to uppercase
        
    def test_valid_stock_symbol_with_spaces(self):
        """Test parsing with leading/trailing spaces"""
        assert get_stock_symbol_from_command("  #2884  ") == ("2884", "TW")
        assert get_stock_symbol_from_command("\t#2330\n") == ("2330", "TW")
        assert get_stock_symbol_from_command("  #AAPL  ") == ("AAPL", "US")
        
    def test_invalid_formats(self):
        """Test various invalid formats"""
        assert get_stock_symbol_from_command("2884") is None  # No # prefix
        assert get_stock_symbol_from_command("#") is None  # Just #
        assert get_stock_symbol_from_command("##2884") is None  # Double #
        assert get_stock_symbol_from_command("hello #2884") is None  # # not at start
        assert get_stock_symbol_from_command("") is None  # Empty string
        assert get_stock_symbol_from_command("#2884 extra text") == ("2884extratext", "TW")  # extra space is removed
        assert get_stock_symbol_from_command("#AAPL extra text") == ("AAPLEXTRATEXT", "US")  # extra space is removed and symbol is converted to uppercase
        
    def test_edge_cases(self):
        """Test edge cases"""
        assert get_stock_symbol_from_command("#0") == ("0", "TW")
        assert get_stock_symbol_from_command("#123456") == ("123456", "TW")  # Long number
        assert get_stock_symbol_from_command("#A") == ("A", "US")  # Single letter
        assert get_stock_symbol_from_command("#ABC123") == ("ABC123", "US")  # Mixed alphanumeric


class TestGetTwStockPrice:
    """Test cases for get_tw_stock_price function"""
    
    @patch('src.quote.tw_stock.get_tw_stock_name')
    @patch('src.quote.tw_stock.yf.Ticker')
    def test_successful_stock_fetch_with_yfinance(self, mock_ticker_class, mock_get_tw_stock_name):
        """Test successful stock price fetch using yfinance"""
        # Mock the ticker instance
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker
        
        # Mock get_tw_stock_name to return the expected name
        mock_get_tw_stock_name.return_value = '台積電'
        
        # Mock the info and history
        mock_ticker.info = {
            'shortName': 'Taiwan Semiconductor',
            'currency': 'TWD',
            'regularMarketPrice': 525,
            'regularMarketPreviousClose': 510
        }
        
        # Mock history DataFrame
        import pandas as pd
        mock_history = pd.DataFrame({
            'Close': [525.0]
        })
        mock_ticker.history.return_value = mock_history
        
        result = get_tw_stock_price("2330")
        
        assert result is not None
        assert result['symbol'] == "2330"
        assert result['name'] == '台積電'
        assert result['price'] == 525.0
        assert result['currency'] == 'TWD'
        assert result['upsOrDowns'] == 1
    
    @patch('src.quote.tw_stock.yf.Ticker')
    def test_stock_not_found_yfinance(self, mock_ticker_class):
        """Test when stock symbol is not found with yfinance"""
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker
        
        # Empty history and no info
        import pandas as pd
        mock_ticker.history.return_value = pd.DataFrame()
        mock_ticker.info = {}
        
        result = get_tw_stock_price("9999")
        assert result is None
    
    @patch('src.quote.tw_stock.yf')
    @patch('src.quote.tw_stock._fallback_stock_price')
    def test_fallback_when_yfinance_fails(self, mock_fallback, mock_yf):
        """Test fallback method when yfinance fails"""
        # Make yfinance raise an exception
        mock_yf.Ticker.side_effect = Exception("yfinance error")
        
        # Mock fallback to return data
        mock_fallback.return_value = {
            'symbol': '2884',
            'name': 'Stock 2884',
            'price': 25.5,
            'currency': 'TWD'
        }
        
        result = get_tw_stock_price("2884")
        
        assert result is not None
        assert result['symbol'] == "2884"
        mock_fallback.assert_called_once_with("2884")
    
    @patch('src.quote.tw_stock.requests.get')
    def test_fallback_twse_api(self, mock_get):
        """Test fallback using TWSE API"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'stat': 'OK',
            'data': [
                ['20231031', '25.50', '26.00', '25.00', '25.30', '1000']
            ]
        }
        mock_get.return_value = mock_response
        
        result = _fallback_stock_price("2884")
        
        assert result is not None
        assert result['symbol'] == "2884"
        assert result['price'] == 25.50


class TestGetUsStockPrice:
    """Test cases for get_us_stock_price function"""
    
    @patch('src.quote.us_stock.yf.Ticker')
    def test_successful_us_stock_fetch(self, mock_ticker_class):
        """Test successful US stock price fetch using yfinance"""
        # Mock the ticker instance
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker
        
        # Mock the info and history
        mock_ticker.info = {
            'shortName': 'Apple Inc.',
            'currency': 'USD',
            'regularMarketPrice': 150,
            'regularMarketPreviousClose': 152
        }
        
        # Mock history DataFrame
        import pandas as pd
        mock_history = pd.DataFrame({
            'Close': [150.0]
        })
        mock_ticker.history.return_value = mock_history
        
        result = get_us_stock_price("AAPL")
        
        assert result is not None
        assert result['symbol'] == "AAPL"
        assert result['name'] == 'Apple Inc.'
        assert result['price'] == 150.0
        assert result['currency'] == 'USD'
        assert result['upsOrDowns'] == -1
    
    @patch('src.quote.us_stock.yf.Ticker')
    def test_us_stock_not_found(self, mock_ticker_class):
        """Test when US stock symbol is not found"""
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker
        
        # Empty history and no info
        import pandas as pd
        mock_ticker.history.return_value = pd.DataFrame()
        mock_ticker.info = {}
        
        result = get_us_stock_price("INVALID")
        assert result is None
    
    @patch('src.quote.us_stock.yf.Ticker')
    def test_us_stock_yfinance_error(self, mock_ticker_class):
        """Test when yfinance fails for US stocks"""
        mock_ticker_class.side_effect = Exception("API error")
        
        result = get_us_stock_price("AAPL")
        assert result is None


class TestGetStockInfo:
    """Test cases for parse_line_command function"""
    
    @patch('src.line.command.get_tw_stock_price')
    def test_tw_stock_info(self, mock_get_tw_price):
        """Test getting Taiwan stock info"""
        mock_get_tw_price.return_value = {
            'symbol': '2884',
            'name': 'Yuanta Financial',
            'price': 25.5,
            'currency': 'TWD'
        }
        
        result = parse_line_command("#2884")
        
        assert result['symbol'] == '2884'
        assert result['name'] == 'Yuanta Financial'
        mock_get_tw_price.assert_called_once_with("2884")
    
    @patch('src.line.command.get_us_stock_price')
    def test_us_stock_info(self, mock_get_us_price):
        """Test getting US stock info"""
        mock_get_us_price.return_value = {
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'price': 150.0,
            'currency': 'USD'
        }
        
        result = parse_line_command("#AAPL")
        
        assert result['symbol'] == 'AAPL'
        assert result['name'] == 'Apple Inc.'
        mock_get_us_price.assert_called_once_with("AAPL")
    
    def test_non_stock_command(self):
        """Test non-stock commands return None"""
        assert parse_line_command("Hello world") is None
        assert parse_line_command("2884") is None
        assert parse_line_command("") is None
    
    @patch('src.line.command.get_tw_stock_price')
    def test_tw_stock_not_found(self, mock_get_tw_price):
        """Test when Taiwan stock is not found"""
        mock_get_tw_price.return_value = None
        
        result = parse_line_command("#9999")
        
        assert result is None
        mock_get_tw_price.assert_called_once_with("9999")
    
    @patch('src.line.command.get_us_stock_price')
    def test_us_stock_not_found(self, mock_get_us_price):
        """Test when US stock is not found"""
        mock_get_us_price.return_value = None
        
        result = parse_line_command("#INVALID")
        
        assert result is None
        mock_get_us_price.assert_called_once_with("INVALID")


if __name__ == "__main__":
    pytest.main([__file__])
