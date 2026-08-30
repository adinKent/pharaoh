import pytest

from routing.acceptance import AcceptanceReport, assert_acceptance_threshold, evaluate_routes
from routing.evaluation import EVALUATION_CASES, EVALUATION_SET_VERSION
from routing.models import Capability, ExecutionPlan, Freshness


def test_evaluation_set_is_versioned():
    assert EVALUATION_SET_VERSION == "v1"
    assert len(EVALUATION_CASES) == len(set(case.message for case in EVALUATION_CASES))


def test_acceptance_report_calculates_accuracy_and_threshold():
    expected = [((Capability.KNOWLEDGE,), Freshness.STATIC), ((Capability.MARKET_DATA,), Freshness.REALTIME)]
    actual = [
        ExecutionPlan(capabilities=[Capability.KNOWLEDGE], freshness=Freshness.STATIC, model_tier="cheap"),
        ExecutionPlan(capabilities=[Capability.MARKET_DATA], freshness=Freshness.REALTIME, model_tier="cheap"),
    ]

    report = evaluate_routes(expected, actual)

    assert report == AcceptanceReport(total=2, passed=2)
    assert_acceptance_threshold(report)


def test_acceptance_threshold_fails_for_insufficient_accuracy():
    with pytest.raises(AssertionError, match="below"):
        assert_acceptance_threshold(AcceptanceReport(total=20, passed=10))
