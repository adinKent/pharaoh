import pytest
from unittest.mock import patch, Mock
import sys
import os

# Add src directory to path so we can import stock_parser
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from stock_parser import parse_stock_command, get_tw_stock_price, get_us_stock_price, get_stock_info

# Mock yfinance at module level
sys.modules['yfinance'] = Mock()


class TestParseStockCommand:
    """Test cases for parse_stock_command function"""
    
    def test_valid_stock_symbol(self):
        """Test parsing valid stock symbols starting with #"""
        assert parse_stock_command("#2884") == ("2884", "TW")
        assert parse_stock_command("#2330") == ("2330", "TW")
        assert parse_stock_command("#1234") == ("1234", "TW")
        assert parse_stock_command("#AAPL") == ("AAPL", "US")
        assert parse_stock_command("#TSLA") == ("TSLA", "US")
        assert parse_stock_command("#aapl") == ("AAPL", "US")  # Should convert to uppercase
        
    def test_valid_stock_symbol_with_spaces(self):
        """Test parsing with leading/trailing spaces"""
        assert parse_stock_command("  #2884  ") == ("2884", "TW")
        assert parse_stock_command("\t#2330\n") == ("2330", "TW")
        assert parse_stock_command("  #AAPL  ") == ("AAPL", "US")
        
    def test_invalid_formats(self):
        """Test various invalid formats"""
        assert parse_stock_command("2884") is None  # No # prefix
        assert parse_stock_command("#") is None  # Just #
        assert parse_stock_command("##2884") is None  # Double #
        assert parse_stock_command("hello #2884") is None  # # not at start
        assert parse_stock_command("") is None  # Empty string
        assert parse_stock_command("#2884 extra text") == ("2884", "TW")  # Should still work
        assert parse_stock_command("#AAPL extra text") == ("AAPL", "US")  # Should still work
        
    def test_edge_cases(self):
        """Test edge cases"""
        assert parse_stock_command("#0") == ("0", "TW")
        assert parse_stock_command("#123456") == ("123456", "TW")  # Long number
        assert parse_stock_command("#A") == ("A", "US")  # Single letter
        assert parse_stock_command("#ABC123") == ("ABC123", "US")  # Mixed alphanumeric


class TestGetTwStockPrice:
    """Test cases for get_tw_stock_price function"""
    
    @patch('stock_parser.yf.Ticker')
    def test_successful_stock_fetch_with_yfinance(self, mock_ticker_class):
        """Test successful stock price fetch using yfinance"""
        # Mock the ticker instance
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker
        
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
    
    @patch('stock_parser.yf.Ticker')
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
    
    @patch('stock_parser.yf')
    @patch('stock_parser._fallback_stock_price')
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
    
    @patch('stock_parser.requests.get')
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
        
        from stock_parser import _fallback_stock_price
        result = _fallback_stock_price("2884")
        
        assert result is not None
        assert result['symbol'] == "2884"
        assert result['price'] == 25.50


class TestGetUsStockPrice:
    """Test cases for get_us_stock_price function"""
    
    @patch('stock_parser.yf.Ticker')
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
    
    @patch('stock_parser.yf.Ticker')
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
    
    @patch('stock_parser.yf.Ticker')
    def test_us_stock_yfinance_error(self, mock_ticker_class):
        """Test when yfinance fails for US stocks"""
        mock_ticker_class.side_effect = Exception("API error")
        
        result = get_us_stock_price("AAPL")
        assert result is None


class TestGetStockInfo:
    """Test cases for get_stock_info function"""
    
    @patch('stock_parser.get_tw_stock_price')
    def test_tw_stock_info(self, mock_get_tw_price):
        """Test getting Taiwan stock info"""
        mock_get_tw_price.return_value = {
            'symbol': '2884',
            'name': 'Yuanta Financial',
            'price': 25.5,
            'currency': 'TWD'
        }
        
        result = get_stock_info("#2884")
        
        assert result['symbol'] == '2884'
        assert result['name'] == 'Yuanta Financial'
        mock_get_tw_price.assert_called_once_with("2884")
    
    @patch('stock_parser.get_us_stock_price')
    def test_us_stock_info(self, mock_get_us_price):
        """Test getting US stock info"""
        mock_get_us_price.return_value = {
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'price': 150.0,
            'currency': 'USD'
        }
        
        result = get_stock_info("#AAPL")
        
        assert result['symbol'] == 'AAPL'
        assert result['name'] == 'Apple Inc.'
        mock_get_us_price.assert_called_once_with("AAPL")
    
    def test_non_stock_command(self):
        """Test non-stock commands return None"""
        assert get_stock_info("Hello world") is None
        assert get_stock_info("2884") is None
        assert get_stock_info("") is None
    
    @patch('stock_parser.get_tw_stock_price')
    def test_tw_stock_not_found(self, mock_get_tw_price):
        """Test when Taiwan stock is not found"""
        mock_get_tw_price.return_value = None
        
        result = get_stock_info("#9999")
        
        assert result is None
        mock_get_tw_price.assert_called_once_with("9999")
    
    @patch('stock_parser.get_us_stock_price')
    def test_us_stock_not_found(self, mock_get_us_price):
        """Test when US stock is not found"""
        mock_get_us_price.return_value = None
        
        result = get_stock_info("#INVALID")
        
        assert result is None
        mock_get_us_price.assert_called_once_with("INVALID")


if __name__ == "__main__":
    pytest.main([__file__])
