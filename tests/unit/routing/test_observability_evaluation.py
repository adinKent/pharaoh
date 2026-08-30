from routing.evaluation import EVALUATION_CASES
from routing.models import Capability, ExecutionPlan, FinancialContext, Freshness
from routing.observability import anonymize_user_id, routing_log_fields


def test_observability_excludes_raw_user_message():
    ctx = FinancialContext(user_id="private-user", message="my sensitive portfolio")
    plan = ExecutionPlan(capabilities=[Capability.PORTFOLIO_ANALYSIS], freshness=Freshness.STATIC, model_tier="strong")

    fields = routing_log_fields(ctx, plan)

    assert "message" not in fields
    assert "sensitive" not in repr(fields)
    assert fields["user_id_hash"] == anonymize_user_id("private-user")


def test_evaluation_set_covers_all_declared_capabilities():
    covered = {capability for case in EVALUATION_CASES for capability in case.expected_capabilities}

    assert covered == set(Capability)
