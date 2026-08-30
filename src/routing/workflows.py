from datetime import UTC, datetime

from routing.models import WorkflowState

WORKFLOW_STEPS = {
    "portfolio_builder": ("risk_profile", "horizon", "allocation", "complete"),
    "company_research": ("entity", "financials", "analysis", "complete"),
    "security_comparison": ("securities", "criteria", "comparison", "complete"),
    "bond_evaluation": ("bond", "issuer", "terms", "analysis", "complete"),
}
TERMINAL_STATES = {"completed", "cancelled", "expired"}


def start_workflow(workflow_id: str, workflow_type: str) -> WorkflowState:
    if workflow_type not in WORKFLOW_STEPS:
        raise ValueError(f"Unknown workflow type: {workflow_type}")
    return WorkflowState(
        workflow_id=workflow_id,
        workflow_type=workflow_type,
        state="active",
        current_step=WORKFLOW_STEPS[workflow_type][0],
        created_at=datetime.now(UTC).isoformat(),
        updated_at=datetime.now(UTC).isoformat(),
    )


def transition_workflow(workflow: WorkflowState, target: str) -> WorkflowState:
    allowed = {"active", "suspended", "completed", "cancelled", "expired"}
    if target not in allowed:
        raise ValueError(f"Unknown workflow state: {target}")
    if workflow.state in TERMINAL_STATES:
        raise ValueError(f"Cannot transition terminal workflow: {workflow.state}")
    return workflow.model_copy(update={"state": target, "updated_at": datetime.now(UTC).isoformat()})


def accept_workflow_input(workflow: WorkflowState, key: str, value: object) -> WorkflowState:
    if workflow.state != "active":
        raise ValueError("Workflow must be active to accept input")
    steps = WORKFLOW_STEPS[workflow.workflow_type]
    try:
        current_index = steps.index(workflow.current_step)
    except ValueError as error:
        raise ValueError(f"Unknown workflow step: {workflow.current_step}") from error
    next_step = steps[min(current_index + 1, len(steps) - 1)]
    next_state = "completed" if next_step == "complete" else "active"
    return workflow.model_copy(
        update={
            "state": next_state,
            "current_step": next_step,
            "collected_inputs": {**workflow.collected_inputs, key: value},
            "updated_at": datetime.now(UTC).isoformat(),
        }
    )
