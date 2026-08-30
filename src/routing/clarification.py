from routing.models import Capability, ExecutionPlan, Freshness


def build_clarification_plan(prompt: str, *, model_tier: str = "cheap") -> ExecutionPlan:
    """Build a plan that asks the user for missing information before tool use."""
    return ExecutionPlan(
        capabilities=[Capability.CLARIFICATION],
        entities=[],
        freshness=Freshness.STATIC,
        tools=[],
        model_tier=model_tier,
    )
