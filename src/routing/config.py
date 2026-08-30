import os


def natural_language_routing_enabled() -> bool:
    """Return whether unmatched natural-language requests use the new router."""
    return os.environ.get("ENABLE_FINANCIAL_ROUTING", "false").strip().lower() in {"1", "true", "yes", "on"}


def safety_mode() -> str:
    """Return the deployment-scoped safety mode."""
    value = os.environ.get("SAFETY_MODE", "off").strip().lower()
    return value if value in {"off", "on"} else "off"
