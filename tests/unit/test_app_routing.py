from unittest.mock import AsyncMock, patch

from routing.models import Capability, ExecutionPlan, Freshness


def test_natural_language_routing_is_disabled_when_flag_is_false(monkeypatch):
    from app import handle_text_message

    monkeypatch.setenv("ENABLE_FINANCIAL_ROUTING", "false")

    event = type("Event", (), {})()
    event.message = type("Message", (), {"text": "What is EPS?", "mark_as_read_token": None})()
    event.reply_token = "reply-token"
    event.source = type("Source", (), {"type": "user", "user_id": "u1"})()

    with patch("app.parse_line_command", return_value=None), patch("app.financial_router.route_line_request", new_callable=AsyncMock) as route:
        handle_text_message(event)

    route.assert_not_called()


def test_natural_language_routing_uses_router_when_enabled(monkeypatch):
    from app import handle_text_message

    event = type("Event", (), {})()
    event.message = type("Message", (), {"text": "What is EPS?", "mark_as_read_token": None})()
    event.reply_token = "reply-token"
    event.source = type("Source", (), {"type": "user", "user_id": "u1"})()
    plan = ExecutionPlan(capabilities=[Capability.KNOWLEDGE], freshness=Freshness.STATIC, model_tier="cheap")
    monkeypatch.setenv("ENABLE_FINANCIAL_ROUTING", "true")

    with (
        patch("app.parse_line_command", return_value=None),
        patch("app.financial_router.route_line_request", new_callable=AsyncMock, return_value=plan) as route,
        patch("app.send_reply_message") as send_reply,
    ):
        handle_text_message(event)

    route.assert_awaited_once()
    send_reply.assert_called_once()
