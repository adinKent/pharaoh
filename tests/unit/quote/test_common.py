import pytest
import sys
import os

# Add project root to path so we can import from src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../src'))

from quote.common import get_ups_or_downs


class TestGetUpsOrDowns:
    """Test cases for get_ups_or_downs function"""
    
    def test_price_up(self):
        """Test when current price is higher than previous close"""
        assert get_ups_or_downs(150.0, 140.0) == 1
        assert get_ups_or_downs(100.5, 100.0) == 1
    
    def test_price_down(self):
        """Test when current price is lower than previous close"""
        assert get_ups_or_downs(140.0, 150.0) == -1
        assert get_ups_or_downs(100.0, 100.5) == -1
    
    def test_price_unchanged(self):
        """Test when current price equals previous close"""
        assert get_ups_or_downs(150.0, 150.0) == 0
        assert get_ups_or_downs(100.0, 100.0) == 0
    
    def test_edge_cases(self):
        """Test edge cases"""
        assert get_ups_or_downs(0.01, 0.0) == 1
        assert get_ups_or_downs(0.0, 0.01) == -1
        assert get_ups_or_downs(0.0, 0.0) == 0


if __name__ == "__main__":
    pytest.main([__file__])

