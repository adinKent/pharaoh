import asyncio
from unittest.mock import patch

from routing.models import Capability, ExecutionPlan, FinancialContext, Freshness
from routing.router import FinancialRouter


def test_line_entrypoint_preserves_fixed_command_response():
    router = FinancialRouter()
    ctx = FinancialContext(user_id="u1", message="#2330")

    with patch("line.command_parser.parse_line_command", return_value="legacy quote") as parse_command:
        result = asyncio.run(router.route_line_request(ctx))

    assert result == "legacy quote"
    parse_command.assert_called_once_with("#2330", False)


def test_line_entrypoint_routes_unmatched_message_to_new_router():
    router = FinancialRouter()
    ctx = FinancialContext(user_id="u1", message="What is EPS?")

    with patch("line.command_parser.parse_line_command", return_value=None):
        result = asyncio.run(router.route_line_request(ctx, is_one_to_one=True))

    assert isinstance(result, ExecutionPlan)
    assert result.capabilities == [Capability.CLARIFICATION]
    assert result.freshness == Freshness.STATIC
