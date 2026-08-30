from dataclasses import dataclass
from datetime import UTC, datetime, time, timedelta
from zoneinfo import ZoneInfo

from routing.models import Freshness
from routing.tool_results import ToolResult


@dataclass(frozen=True)
class FreshnessAssessment:
    freshness: Freshness
    is_acceptable: bool
    is_market_open: bool
    reason: str = ""


def _parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
    except ValueError:
        return None


def market_is_open(market: str, now: datetime) -> bool:
    zone = ZoneInfo("America/New_York") if market.upper() == "US" else ZoneInfo("Asia/Taipei")
    local = now.astimezone(zone)
    if local.weekday() >= 5:
        return False
    if market.upper() == "US":
        return time(9, 30) <= local.time() <= time(16, 0)
    return time(9, 0) <= local.time() <= time(13, 30)


def assess_realtime(effective_at: str | None, *, market: str, now: datetime | None = None) -> FreshnessAssessment:
    now = now or datetime.now(UTC)
    effective = _parse_time(effective_at)
    open_now = market_is_open(market, now)
    if effective is None:
        return FreshnessAssessment(Freshness.REALTIME, False, open_now, "Missing effective time")
    age = now - effective
    if age < timedelta(0):
        return FreshnessAssessment(Freshness.REALTIME, False, open_now, "Effective time is in the future")
    if open_now and age > timedelta(minutes=5):
        return FreshnessAssessment(Freshness.REALTIME, False, True, "Quote exceeds five-minute realtime limit")
    return FreshnessAssessment(Freshness.REALTIME, True, open_now)


def apply_freshness(result: ToolResult, required: Freshness, *, market: str = "US", now: datetime | None = None) -> ToolResult:
    if required != Freshness.REALTIME:
        return result
    assessment = assess_realtime(result.effective_at, market=market, now=now)
    result.is_stale = not assessment.is_acceptable
    if result.is_stale and not result.error:
        result.error = assessment.reason
        result.quality = "stale"
    return result
