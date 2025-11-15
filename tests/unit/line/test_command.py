import pytest
from unittest.mock import patch, Mock
import sys
import os

# Add project root to path so we can import from src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from src.line.command_parser import get_stock_symbol_from_command, parse_line_command


class TestGetStockSymbolFromCommand:
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


class TestParseLineCommand:
    """Test cases for parse_line_command function"""
    
    @patch('src.line.command_parser.get_tw_stock_price')
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
    
    @patch('src.line.command_parser.get_us_stock_price')
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
    
    @patch('src.line.command_parser.get_tw_stock_price')
    def test_tw_stock_not_found(self, mock_get_tw_price):
        """Test when Taiwan stock is not found"""
        mock_get_tw_price.return_value = None
        
        result = parse_line_command("#9999")
        
        assert result is None
        mock_get_tw_price.assert_called_once_with("9999")
    
    @patch('src.line.command_parser.get_us_stock_price')
    def test_us_stock_not_found(self, mock_get_us_price):
        """Test when US stock is not found"""
        mock_get_us_price.return_value = None
        
        result = parse_line_command("#INVALID")
        
        assert result is None
        mock_get_us_price.assert_called_once_with("INVALID")


if __name__ == "__main__":
    pytest.main([__file__])

