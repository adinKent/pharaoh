from routing.entities import resolve_entities_in_text
from routing.models import Capability, FinancialContext, Freshness, RouteCandidate


async def semantic_route(ctx: FinancialContext) -> RouteCandidate | None:
    """Classify common finance request shapes without an external model call."""
    text = ctx.message.lower()
    if any(term in text for term in ("台股", "台灣股市", "台股大盤")):
        freshness = Freshness.RECENT if any(term in text for term in ("最近", "近期", "近來", "recent", "lately")) else Freshness.STATIC
        return RouteCandidate(capability=Capability.MARKET_DATA, confidence=0.92, freshness=freshness)
    if any(term in text for term in ("eps", "本益比", "殖利率是什麼", "what is")):
        return RouteCandidate(capability=Capability.KNOWLEDGE, confidence=0.9)
    if resolve_entities_in_text(ctx.message) and any(term in text for term in ("營運", "基本面", "財報", "公司", "fundamental", "operations")):
        return RouteCandidate(capability=Capability.COMPANY_ANALYSIS, confidence=0.9, freshness=Freshness.RECENT)
    return None
