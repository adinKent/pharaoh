from unittest.mock import patch

from routing.executor import FinancialExecutor
from routing.models import Capability, EntityKind, EntityReference, ExecutionPlan, Freshness
from routing.tool_results import ToolResult


def test_executor_answers_clarification_without_tools():
    plan = ExecutionPlan(capabilities=[Capability.CLARIFICATION], freshness=Freshness.STATIC, model_tier="cheap")

    assert "更明確" in FinancialExecutor().execute(plan, query="比較")


def test_executor_renders_simple_market_data():
    entity = EntityReference(kind=EntityKind.SECURITY, canonical_id="US:AAPL", symbol="AAPL", market="US", display_name="Apple", confidence=1)
    plan = ExecutionPlan(
        capabilities=[Capability.MARKET_DATA], entities=[entity], freshness=Freshness.RECENT, tools=["market_data"], model_tier="cheap"
    )

    mock_market = patch(
        "routing.executor.TOOL_REGISTRY",
        {
            "market_data": lambda _: ToolResult(
                data={"price": 100},
                source="quote",
                retrieved_at="2026-08-30T12:00:00Z",
                effective_at="2026-08-30T11:59:00Z",
            )
        },
    )
    with mock_market:
        result = FinancialExecutor().execute(plan, query="AAPL price")

    assert '"price": 100' in result
    assert "來源：quote" in result
