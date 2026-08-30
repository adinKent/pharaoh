import os

DEFAULT_MODEL_TIERS = {
    "cheap": "",
    "medium": "",
    "strong": "",
}


def model_for_tier(tier: str) -> str:
    """Resolve a tier through deployment configuration without provider coupling."""
    if tier not in DEFAULT_MODEL_TIERS:
        raise ValueError(f"Unknown model tier: {tier}")
    return os.environ.get(f"FINANCIAL_MODEL_{tier.upper()}", DEFAULT_MODEL_TIERS[tier])
