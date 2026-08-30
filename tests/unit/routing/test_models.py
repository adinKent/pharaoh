import pytest
from pydantic import ValidationError

from routing.models import Capability, EntityKind, EntityReference, ExecutionPlan, Freshness
from routing.tool_results import ToolResult


def test_execution_plan_accepts_typed_entities_and_model_tier():
    plan = ExecutionPlan(
        capabilities=[Capability.MARKET_DATA],
        entities=[
            EntityReference(
                kind=EntityKind.SECURITY,
                canonical_id="US:AAPL",
                symbol="AAPL",
                market="US",
                display_name="Apple",
                confidence=0.99,
            )
        ],
        freshness=Freshness.REALTIME,
        tools=["market_data"],
        model_tier="cheap",
    )

    assert plan.entities[0].canonical_id == "US:AAPL"


def test_execution_plan_rejects_unknown_model_tier():
    with pytest.raises(ValidationError):
        ExecutionPlan(capabilities=[Capability.KNOWLEDGE], freshness=Freshness.STATIC, model_tier="unknown")


def test_tool_result_preserves_provenance_and_error():
    result = ToolResult[str](
        data=None,
        source="test-source",
        retrieved_at="2026-08-30T12:00:00Z",
        effective_at="2026-08-30T11:59:00Z",
        quality="unavailable",
        error="timeout",
    )

    assert result.error == "timeout"
    assert result.effective_at == "2026-08-30T11:59:00Z"
