import re

from routing.models import Capability, Freshness


class RoutingSignal:
    def __init__(self, capability: Capability, confidence: float, freshness: Freshness | None = None):
        self.capability = capability
        self.confidence = confidence
        self.freshness = freshness


_REALTIME = r"今天|現在|目前|即時|最新價格|現價|now|today|right now|current price"
_COMPARISON = r"比較|對比|哪一檔|哪個比較好|\bvs\.?\b|compare"
_DIVIDEND = r"殖利率|配息|股息|股利|dividend|payout"
_BOND = r"債券|bond|senior unsecured|到期殖利率|coupon"
_PORTFOLIO = r"投資組合|資產配置|退休|portfolio|allocation|retirement"
_NEWS = r"新聞|消息|公告|事件|news|announcement|what caused"


def route_signals(message: str) -> list[RoutingSignal]:
    """Return high-confidence hints without constructing an execution plan."""
    text = (message or "").lower()
    signals: list[RoutingSignal] = []

    if re.search(_COMPARISON, text, flags=re.IGNORECASE):
        signals.append(RoutingSignal(Capability.SECURITY_COMPARISON, 0.95))
    if re.search(_PORTFOLIO, text, flags=re.IGNORECASE):
        signals.append(RoutingSignal(Capability.PORTFOLIO_ANALYSIS, 0.95))
    if re.search(_BOND, text, flags=re.IGNORECASE):
        signals.append(RoutingSignal(Capability.BOND_ANALYSIS, 0.95))
    if re.search(_DIVIDEND, text, flags=re.IGNORECASE):
        signals.append(RoutingSignal(Capability.DIVIDEND_ANALYSIS, 0.9))
    if re.search(_NEWS, text, flags=re.IGNORECASE):
        signals.append(RoutingSignal(Capability.FINANCIAL_NEWS, 0.9))
    if re.search(_REALTIME, text, flags=re.IGNORECASE):
        signals.append(RoutingSignal(Capability.MARKET_DATA, 0.95, Freshness.REALTIME))

    return signals
