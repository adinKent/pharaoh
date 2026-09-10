from routing.clarification import build_clarification_plan
from routing.entities import resolve_entities_in_text, resolve_entity
from routing.models import Capability, EntityKind, Freshness
from routing.rules import route_signals


def test_resolve_us_security_to_market_aware_canonical_id():
    result = resolve_entity("aapl")

    assert result.ambiguous is False
    assert result.entities[0].canonical_id == "US:AAPL"
    assert result.entities[0].kind == EntityKind.SECURITY


def test_resolve_fixed_multi_index_alias_as_ambiguous():
    result = resolve_entity("美股")

    assert result.ambiguous is True
    assert len(result.entities) == 4


def test_resolve_taiwan_market_as_index_entity():
    result = resolve_entity("台股")

    assert result.ambiguous is False
    assert result.entities[0].canonical_id == "TW:IX0001"
    assert result.entities[0].kind == EntityKind.INDEX


def test_resolve_taiwan_company_name_as_issuer():
    result = resolve_entities_in_text("國泰金的營運狀況")

    assert result[0].canonical_id == "TW:2882"
    assert result[0].kind == EntityKind.ISSUER


def test_rules_keep_overlapping_signals_instead_of_returning_one_capability():
    signals = route_signals("GAIN 今天的股息殖利率")

    assert {signal.capability for signal in signals} == {Capability.DIVIDEND_ANALYSIS, Capability.MARKET_DATA}
    assert next(signal for signal in signals if signal.capability == Capability.MARKET_DATA).freshness == Freshness.REALTIME


def test_rules_support_chinese_and_english_comparison():
    assert route_signals("Compare AAPL vs MSFT")[0].capability == Capability.SECURITY_COMPARISON


def test_clarification_plan_has_no_financial_tools():
    plan = build_clarification_plan("Which market do you mean?")

    assert plan.capabilities == [Capability.CLARIFICATION]
    assert plan.tools == []
