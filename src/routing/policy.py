from routing.config import safety_mode


def policy_context() -> dict[str, str]:
    """Expose the active deployment policy for logging and answer generation."""
    mode = safety_mode()
    return {
        "safety_mode": mode,
        "advice_boundaries": "enabled" if mode == "on" else "disabled",
    }


def apply_safety_policy(answer: str, *, request: str) -> str:
    """Apply deployment policy to recommendation-shaped answers."""
    if safety_mode() == "off":
        return answer
    lowered = request.lower()
    if any(term in lowered for term in ("should i buy", "該買", "退休", "投資組合", "portfolio")):
        return "本回答僅供資訊與情境分析，請依個人風險承受度及投資目標自行判斷。\n" + answer
    return answer
