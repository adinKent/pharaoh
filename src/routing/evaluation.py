from dataclasses import dataclass

from routing.models import Capability, Freshness

EVALUATION_SET_VERSION = "v1"


@dataclass(frozen=True)
class RoutingCase:
    message: str
    expected_capabilities: tuple[Capability, ...]
    expected_freshness: Freshness


EVALUATION_CASES = tuple(
    RoutingCase(message, (capability,), freshness)
    for message, capability, freshness in (
        ("What is EPS?", Capability.KNOWLEDGE, Freshness.STATIC),
        ("AAPL price now", Capability.MARKET_DATA, Freshness.REALTIME),
        ("Analyze AAPL company", Capability.COMPANY_ANALYSIS, Freshness.STATIC),
        ("Analyze AAPL security", Capability.SECURITY_ANALYSIS, Freshness.STATIC),
        ("Compare AAPL vs MSFT", Capability.SECURITY_COMPARISON, Freshness.STATIC),
        ("Build a retirement portfolio", Capability.PORTFOLIO_ANALYSIS, Freshness.STATIC),
        ("AAPL dividend safety", Capability.DIVIDEND_ANALYSIS, Freshness.STATIC),
        ("Explain this bond", Capability.BOND_ANALYSIS, Freshness.STATIC),
        ("Latest AAPL news", Capability.FINANCIAL_NEWS, Freshness.STATIC),
        ("Research AAPL across sources", Capability.WEB_RESEARCH, Freshness.STATIC),
        ("Which one?", Capability.CLARIFICATION, Freshness.STATIC),
    )
)
