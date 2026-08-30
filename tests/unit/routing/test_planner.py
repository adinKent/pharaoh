from routing.models import Capability, ExecutionPlan, Freshness
from routing.models_config import model_for_tier
from routing.planner import build_execution_graph


def test_execution_graph_deduplicates_tools_from_plan():
    plan = ExecutionPlan(
        capabilities=[Capability.COMPANY_ANALYSIS, Capability.DIVIDEND_ANALYSIS],
        freshness=Freshness.RECENT,
        tools=["financial_statements", "market_data"],
        model_tier="strong",
    )

    graph = build_execution_graph(plan)

    assert [node.operation for node in graph.nodes] == ["financial_statements", "market_data", "generate_answer"]
    assert graph.nodes[-1].depends_on == ["tool-1", "tool-2"]


def test_model_tier_is_deployment_configured(monkeypatch):
    monkeypatch.setenv("FINANCIAL_MODEL_STRONG", "configured-strong-model")

    assert model_for_tier("strong") == "configured-strong-model"
