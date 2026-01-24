import sys
from unittest.mock import Mock, patch

import pytest
import pandas as pd

from quote.tw_stock import _fallback_stock_price, get_tw_stock_price

# Mock yfinance at module level
sys.modules['yfinance'] = Mock()

class TestGetTwStockPrice:
    """Test cases for get_tw_stock_price function"""

    @patch('quote.tw_stock.yf.Ticker')
    @patch('quote.tw_stock.quote_stock')
    def test_successful_stock_fetch_with_yfinance(self, mock_fugle_quote_stock, mock_ticker_class):
        """Test successful stock price fetch using fugle and yfinance"""
        # Mock quote result from fugle
        mock_fugle_quote_stock.return_value = {
            "exchange": "TWSE",
            "symbol": "2330",
            "name": "台積電",
            "lastPrice": 525.0,
            "previousClose": 510.0
        }

        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker

        # Mock the yahoo finance info and history
        mock_ticker.info = {
            "shortName": "Taiwan Semiconductor",
            "currentPrice": 525,
            "regularMarketPrice": 525,
            "regularMarketPreviousClose": 510,
            "currency": "TWD",
        }

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
        mock_fugle_quote_stock.assert_called_once_with("2330")

    @patch('quote.tw_stock.yf.Ticker')
    def test_stock_not_found_yfinance(self, mock_ticker_class):
        """Test when stock symbol is not found with yfinance"""
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker

        # Empty history and no info
        mock_ticker.history.return_value = pd.DataFrame()
        mock_ticker.info = {}

        result = get_tw_stock_price("9999")
        assert result is None

    @patch('quote.tw_stock.quote_stock')
    @patch('quote.tw_stock._fallback_stock_price')
    def test_fallback_when_fugle_fails(self, mock_fallback, mock_fugle_quote_stock):
        """Test fallback method when fugleyfinance fails"""
        # Make yfinance raise an exception
        mock_fugle_quote_stock.side_effect = Exception("fugle error")

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


    @patch('quote.tw_stock.yf')
    @patch('quote.tw_stock._fallback_stock_price')
    def test_fallback_when_yfinance_fails(self, mock_fallback, mock_yf):
        """Test fallback method when fugleyfinance fails"""
        # Make yfinance raise an exception
        mock_yf.Ticker.side_effect = Exception("yfinance error")

        # Mock fallback to return data
        mock_fallback.return_value = {
            'symbol': '2884',
            'name': 'Stock 2884',
            'price': 25.5,
            'currency': 'TWD'
        }

        result = get_tw_stock_price("2884", "2d")

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
