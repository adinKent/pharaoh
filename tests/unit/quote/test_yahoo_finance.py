from unittest.mock import Mock, patch

import pandas as pd
import pytest

from quote.yahoo_finance import quote_stock


class TestQuoteStock:
    """Test cases for quote_stock function"""

    @patch('quote.yahoo_finance.yf.Ticker')
    def test_successful_stock_fetch(self, mock_ticker_class):
        """Test successful stock price fetch using yfinance"""
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

        result = quote_stock("AAPL")

        assert result is not None
        assert result['symbol'] == "AAPL"
        assert result['name'] == 'Apple Inc.'
        assert result['price'] == 150.0
        assert result['currency'] == 'USD'
        assert result['upsOrDowns'] == -1

    @patch('quote.yahoo_finance.yf.Ticker')
    def test_stock_not_found(self, mock_ticker_class):
        """Test when stock symbol is not found"""
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker

        # Empty history and no info
        mock_ticker.history.return_value = pd.DataFrame()
        mock_ticker.info = {}

        result = quote_stock("INVALID")
        assert result is None

    @patch('quote.yahoo_finance.yf.Ticker')
    def test_stock_yfinance_error(self, mock_ticker_class):
        """Test when yfinance fails"""
        mock_ticker_class.side_effect = Exception("API error")

        result = quote_stock("AAPL")
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__])
