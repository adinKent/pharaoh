import asyncio
from types import SimpleNamespace

from routing.llm_router import llm_route
from routing.models import Capability, FinancialContext, Freshness
from routing.semantic import semantic_route


def test_semantic_router_classifies_recent_taiwan_market_request():
    candidate = asyncio.run(semantic_route(FinancialContext(user_id="u1", message="最近台股如何")))

    assert candidate.capability == Capability.MARKET_DATA
    assert candidate.freshness == Freshness.RECENT
    assert candidate.confidence >= 0.85


def test_semantic_router_classifies_taiwan_company_operations():
    candidate = asyncio.run(semantic_route(FinancialContext(user_id="u1", message="國泰金的營運狀況")))

    assert candidate.capability == Capability.COMPANY_ANALYSIS
    assert candidate.freshness == Freshness.RECENT


def test_llm_router_parses_structured_response_without_exposing_reasoning():
    response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    content='{"capabilities":["company_analysis"],"confidence":0.91,"freshness":"recent","requires_financial_statements":true}'
                )
            )
        ]
    )

    class Completions:
        def create(self, **kwargs):
            assert kwargs["response_format"] == {"type": "json_object"}
            return response

    client = SimpleNamespace(chat=SimpleNamespace(completions=Completions()))
    decision = asyncio.run(llm_route(FinancialContext(user_id="u1", message="分析公司"), client=client))

    assert decision.capabilities == [Capability.COMPANY_ANALYSIS]
    assert decision.freshness == Freshness.RECENT
    assert decision.reasoning_summary == ""


def test_llm_router_uses_fallback_model_after_main_model_failure():
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content='{"capabilities":["knowledge"],"confidence":0.9,"freshness":"static"}'))]
    )
    models = []

    class Completions:
        def create(self, **kwargs):
            models.append(kwargs["model"])
            if len(models) == 1:
                raise RuntimeError("main model unavailable")
            return response

    client = SimpleNamespace(chat=SimpleNamespace(completions=Completions()))
    decision = asyncio.run(llm_route(FinancialContext(user_id="u1", message="Explain EPS"), client=client))

    assert decision.capabilities == [Capability.KNOWLEDGE]
    assert models[0] == "glm-5.3-flash"
    assert models[1] == "deepseek-v4-flash"


def test_llm_router_normalizes_known_capability_aliases():
    response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    content='{"capabilities":["sector_performance_analysis","news_search"],"confidence":0.9,"freshness":"recent"}'
                )
            )
        ]
    )

    class Completions:
        def create(self, **kwargs):
            return response

    client = SimpleNamespace(chat=SimpleNamespace(completions=Completions()))
    decision = asyncio.run(llm_route(FinancialContext(user_id="u1", message="最近台股表現和新聞"), client=client))

    assert decision.capabilities == [Capability.MARKET_DATA, Capability.FINANCIAL_NEWS]


def test_llm_router_rejects_unknown_capability_after_normalization():
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content='{"capabilities":["made_up_analysis"],"confidence":0.9,"freshness":"static"}'))]
    )

    class Completions:
        def create(self, **kwargs):
            return response

    client = SimpleNamespace(chat=SimpleNamespace(completions=Completions()))

    assert asyncio.run(llm_route(FinancialContext(user_id="u1", message="unknown"), client=client)) is None
