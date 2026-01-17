import sys
from unittest.mock import Mock, patch
import pytest
import pandas as pd

from quote.us_stock import get_us_stock_price

# Mock yfinance at module level
sys.modules['yfinance'] = Mock()

class TestGetUsStockPrice:
    """Test cases for get_us_stock_price function"""

    @patch('quote.us_stock.yf.Ticker')
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

    @patch('quote.us_stock.yf.Ticker')
    def test_us_stock_not_found(self, mock_ticker_class):
        """Test when US stock symbol is not found"""
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker

        # Empty history and no info
        mock_ticker.history.return_value = pd.DataFrame()
        mock_ticker.info = {}

        result = get_us_stock_price("INVALID")
        assert result is None

    @patch('quote.us_stock.yf.Ticker')
    def test_us_stock_yfinance_error(self, mock_ticker_class):
        """Test when yfinance fails for US stocks"""
        mock_ticker_class.side_effect = Exception("API error")

        result = get_us_stock_price("AAPL")
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__])
