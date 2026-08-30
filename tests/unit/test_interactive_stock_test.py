import os
import sys
from unittest.mock import AsyncMock, patch

from routing.models import Capability, ExecutionPlan, Freshness

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def test_process_message_uses_legacy_parser_when_routing_disabled():
    from interactive_stock_test import process_message

    with patch("interactive_stock_test.parse_line_command", return_value="legacy") as parse_command:
        result = process_message("#2330", enable_financial_routing=False)

    assert result == "legacy"
    parse_command.assert_called_once_with("#2330", True)


def test_process_message_uses_financial_router_when_enabled():
    from interactive_stock_test import process_message

    plan = ExecutionPlan(capabilities=[Capability.CLARIFICATION], freshness=Freshness.STATIC, model_tier="cheap")
    with patch("interactive_stock_test.FinancialRouter.route_line_request", new_callable=AsyncMock, return_value=plan) as route:
        result = process_message("What is EPS?", enable_financial_routing=True)

    assert "更明確" in result
    route.assert_awaited_once()
