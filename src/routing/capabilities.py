from dataclasses import dataclass

from routing.models import Capability


@dataclass(frozen=True)
class CapabilityConfig:
    tools: tuple[str, ...]
    model_tier: str


CAPABILITY_CONFIG: dict[Capability, CapabilityConfig] = {
    Capability.KNOWLEDGE: CapabilityConfig((), "cheap"),
    Capability.MARKET_DATA: CapabilityConfig(("market_data",), "cheap"),
    Capability.COMPANY_ANALYSIS: CapabilityConfig(("financial_statements", "market_data"), "strong"),
    Capability.SECURITY_ANALYSIS: CapabilityConfig(("market_data", "financial_statements"), "strong"),
    Capability.SECURITY_COMPARISON: CapabilityConfig(("market_data", "financial_statements"), "strong"),
    Capability.PORTFOLIO_ANALYSIS: CapabilityConfig(("portfolio_calculator", "market_data"), "strong"),
    Capability.DIVIDEND_ANALYSIS: CapabilityConfig(("financial_statements", "market_data"), "strong"),
    Capability.BOND_ANALYSIS: CapabilityConfig(("bond_data", "financial_statements"), "strong"),
    Capability.FINANCIAL_NEWS: CapabilityConfig(("financial_search",), "medium"),
    Capability.WEB_RESEARCH: CapabilityConfig(("financial_search",), "medium"),
    Capability.CLARIFICATION: CapabilityConfig((), "cheap"),
}


_TIER_RANK = {"cheap": 0, "medium": 1, "strong": 2}


def build_capability_requirements(capabilities: list[Capability]) -> tuple[list[str], str]:
    """Merge tool requirements and choose the strongest required model tier."""
    tools: list[str] = []
    tier = "cheap"
    for capability in capabilities:
        config = CAPABILITY_CONFIG[capability]
        for tool in config.tools:
            if tool not in tools:
                tools.append(tool)
        if _TIER_RANK[config.model_tier] > _TIER_RANK[tier]:
            tier = config.model_tier
    return tools, tier


def validate_capability_registry() -> None:
    missing = set(Capability) - set(CAPABILITY_CONFIG)
    if missing:
        raise ValueError(f"Capability configuration is incomplete: {sorted(item.value for item in missing)}")
