import pytest
from unittest.mock import patch, Mock
import sys
import os

# Add project root to path so we can import from src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../src'))

from quote.tw_stock import get_tw_stock_price, _fallback_stock_price

# Mock yfinance at module level
sys.modules['yfinance'] = Mock()


class TestGetTwStockPrice:
    """Test cases for get_tw_stock_price function"""
    
    @patch('quote.tw_stock.get_tw_stock_name')
    @patch('quote.tw_stock.yf.Ticker')
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
    
    @patch('quote.tw_stock.yf.Ticker')
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
    
    @patch('quote.tw_stock.yf')
    @patch('quote.tw_stock._fallback_stock_price')
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
    
    @patch('quote.tw_stock.requests.get')
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


if __name__ == "__main__":
    pytest.main([__file__])
