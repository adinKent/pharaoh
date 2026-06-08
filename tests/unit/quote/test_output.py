import os
import sys

import pytest

from quote.output import format_cash_dividend, format_ex_dividend_response, get_ups_or_downs

# Add project root to path so we can import from src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))


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


class TestFormatExDividendResponse:
    def test_format_ex_dividend_stocks(self):
        result = format_ex_dividend_response(
            [
                {
                    "market": "上市",
                    "symbol": "2330",
                    "name": "台積電",
                    "cashDividend": "4.0",
                },
                {
                    "market": "上櫃",
                    "symbol": "3680",
                    "name": "家登",
                    "cashDividend": "4.99733964",
                },
            ],
            "2026-06-17",
        )

        assert "2026-06-17 今日除息股票 (2 檔):" in result
        assert "台積電 (2330) 現金股利: 4" in result
        assert "家登 (3680) 現金股利: 4.99733964" in result

    def test_format_no_ex_dividend_stocks(self):
        assert format_ex_dividend_response([], "2026-06-07") == "2026-06-07 今日沒有除息股票。"


class TestFormatCashDividend:
    @pytest.mark.parametrize(
        ("cash_dividend", "expected"),
        [
            ("4.0", "4"),
            ("4.00000000", "4"),
            ("4.9973396400", "4.99733964"),
            ("0.0000", "0"),
            ("2.2", "2.2"),
            ("-", "-"),
            ("", "-"),
            (None, "-"),
        ],
    )
    def test_removes_trailing_zeroes(self, cash_dividend, expected):
        assert format_cash_dividend(cash_dividend) == expected


if __name__ == "__main__":
    pytest.main([__file__])
