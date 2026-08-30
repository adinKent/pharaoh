import hashlib
import logging
import os

from routing.models import ExecutionPlan, FinancialContext


def anonymize_user_id(user_id: str) -> str:
    return hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:16]


def routing_log_fields(ctx: FinancialContext, plan: ExecutionPlan, *, confidence: float | None = None) -> dict:
    fields = {
        "user_id_hash": anonymize_user_id(ctx.user_id),
        "conversation_id": ctx.conversation_id,
        "capabilities": [item.value for item in plan.capabilities],
        "entities": [item.canonical_id for item in plan.entities],
        "freshness": plan.freshness.value,
        "tools": plan.tools,
        "model_tier": plan.model_tier,
        "workflow": plan.workflow.workflow_id if plan.workflow else None,
        "safety_mode": os.environ.get("SAFETY_MODE", "off"),
        "latency_ms": None,
        "token_usage": None,
        "data_quality": None,
        "error": None,
    }
    if confidence is not None:
        fields["confidence"] = confidence
    return fields


def log_routing(logger: logging.Logger, ctx: FinancialContext, plan: ExecutionPlan, *, confidence: float | None = None) -> None:
    logger.info("financial_request_routed", extra=routing_log_fields(ctx, plan, confidence=confidence))
