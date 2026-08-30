from routing.answer import answer_data_status, source_note
from routing.config import safety_mode
from routing.data_quality import choose_best_result, conflicting_results, missing_critical_data
from routing.models import Freshness
from routing.policy import apply_safety_policy, policy_context
from routing.tool_results import ToolResult


def _result(data, source="source", stale=False, error=None):
    return ToolResult(
        data=data,
        source=source,
        retrieved_at="2026-08-30T12:00:00Z",
        effective_at="2026-08-30T11:59:00Z",
        is_stale=stale,
        error=error,
    )


def test_choose_best_result_skips_stale_primary_for_fallback():
    result = choose_best_result([_result({"price": 1}, stale=True), _result({"price": 2}, source="fallback")])

    assert result.source == "fallback"


def test_conflicting_results_are_detected():
    assert conflicting_results([_result(1), _result(2, source="fallback")]) is True


def test_missing_critical_data_is_explicit():
    assert missing_critical_data([_result(None, error="timeout")]) is True
    assert "無法做出可靠判斷" in answer_data_status([_result(None, error="timeout")], Freshness.RECENT)


def test_recent_answer_includes_source_and_effective_time():
    note = source_note([_result({"price": 1}, source="primary")], Freshness.RECENT)

    assert "primary" in note
    assert "2026-08-30T11:59:00Z" in note


def test_safety_mode_is_deployment_configured(monkeypatch):
    monkeypatch.setenv("SAFETY_MODE", "on")

    assert safety_mode() == "on"
    assert policy_context() == {"safety_mode": "on", "advice_boundaries": "enabled"}


def test_safety_mode_changes_portfolio_and_buy_answer_behavior(monkeypatch):
    monkeypatch.setenv("SAFETY_MODE", "off")
    assert apply_safety_policy("分析結果", request="Should I buy AAPL?") == "分析結果"

    monkeypatch.setenv("SAFETY_MODE", "on")
    guarded = apply_safety_policy("分析結果", request="Should I buy AAPL?")
    assert guarded.startswith("本回答僅供資訊")
    assert apply_safety_policy("配置結果", request="建立退休投資組合").startswith("本回答僅供資訊")
