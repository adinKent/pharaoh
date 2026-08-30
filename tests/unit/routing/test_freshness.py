from datetime import UTC, datetime

from routing.freshness import apply_freshness, assess_realtime, market_is_open
from routing.models import Freshness
from routing.tool_results import ToolResult


def test_realtime_quote_within_five_minutes_is_acceptable_during_market_hours():
    now = datetime(2026, 8, 28, 14, 2, tzinfo=UTC)  # Friday, 10:02 New York

    result = assess_realtime("2026-08-28T13:59:00Z", market="US", now=now)

    assert result.is_acceptable is True
    assert result.is_market_open is True


def test_realtime_quote_older_than_five_minutes_is_stale_during_market_hours():
    now = datetime(2026, 8, 28, 14, 2, tzinfo=UTC)

    result = assess_realtime("2026-08-28T13:50:00Z", market="US", now=now)

    assert result.is_acceptable is False
    assert "five-minute" in result.reason


def test_outside_market_hours_keeps_last_transaction_acceptable():
    now = datetime(2026, 8, 29, 14, 0, tzinfo=UTC)  # Saturday

    result = assess_realtime("2026-08-28T20:00:00Z", market="US", now=now)

    assert result.is_acceptable is True
    assert result.is_market_open is False
    assert market_is_open("US", now) is False


def test_apply_freshness_marks_stale_tool_result():
    result = ToolResult(data={"price": 1}, source="quote", retrieved_at="2026-08-28T14:00:00Z", effective_at="2026-08-28T13:50:00Z")

    result = apply_freshness(result, Freshness.REALTIME, market="US", now=datetime(2026, 8, 28, 14, 2, tzinfo=UTC))

    assert result.is_stale is True
    assert result.quality == "stale"
