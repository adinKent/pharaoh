import asyncio

from routing.capabilities import CAPABILITY_CONFIG, validate_capability_registry
from routing.models import Capability, EntityKind, FinancialContext, Freshness, RouteCandidate, RouteDecision
from routing.router import FinancialRouter


def test_rules_build_multi_capability_plan_with_deduplicated_tools():
    plan = asyncio.run(FinancialRouter().route(FinancialContext(user_id="u1", message="GAIN 今天的股息殖利率")))

    assert plan.capabilities == [Capability.DIVIDEND_ANALYSIS, Capability.MARKET_DATA]
    assert plan.tools == ["financial_statements", "market_data"]
    assert plan.freshness == Freshness.REALTIME


def test_high_confidence_semantic_candidate_precedes_llm_fallback():
    async def semantic(_ctx):
        return RouteCandidate(capability=Capability.COMPANY_ANALYSIS, confidence=0.9)

    async def llm(_ctx):
        raise AssertionError("LLM fallback should not be called")

    plan = asyncio.run(FinancialRouter(semantic, llm).route(FinancialContext(user_id="u1", message="分析這家公司")))

    assert plan.capabilities == [Capability.COMPANY_ANALYSIS]


def test_low_confidence_semantic_candidate_uses_structured_llm_fallback():
    async def semantic(_ctx):
        return RouteCandidate(capability=Capability.KNOWLEDGE, confidence=0.4)

    async def llm(_ctx):
        return RouteDecision(capabilities=[Capability.SECURITY_COMPARISON], confidence=0.9)

    plan = asyncio.run(FinancialRouter(semantic, llm).route(FinancialContext(user_id="u1", message="哪個比較好")))

    assert plan.capabilities == [Capability.SECURITY_COMPARISON]


def test_active_workflow_continuation_preserves_capability():
    from routing.models import WorkflowState

    ctx = FinancialContext(
        user_id="u1",
        message="20 年",
        current_capabilities=[Capability.PORTFOLIO_ANALYSIS],
        active_workflow=WorkflowState(workflow_id="w1", workflow_type="portfolio_builder", state="active", current_step="horizon"),
    )

    plan = asyncio.run(FinancialRouter().route(ctx))

    assert plan.capabilities == [Capability.PORTFOLIO_ANALYSIS]
    assert plan.workflow.workflow_id == "w1"


def test_all_declared_capabilities_have_configuration():
    validate_capability_registry()
    assert set(CAPABILITY_CONFIG) == set(Capability)
    assert EntityKind.SECURITY.value == "security"
