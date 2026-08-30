from typing import Protocol

from routing.capabilities import build_capability_requirements, validate_capability_registry
from routing.clarification import build_clarification_plan
from routing.entities import resolve_entity
from routing.models import Capability, EntityReference, ExecutionPlan, FinancialContext, Freshness, RouteCandidate, RouteDecision
from routing.rules import route_signals


class SemanticRouter(Protocol):
    async def __call__(self, ctx: FinancialContext) -> RouteCandidate | None: ...


class LLMRouter(Protocol):
    async def __call__(self, ctx: FinancialContext) -> RouteDecision | None: ...


def _extract_entities(ctx: FinancialContext) -> list[EntityReference]:
    """Resolve token-like symbols and retain already resolved conversation entities."""
    entities = list(ctx.known_entities)
    for token in ctx.message.replace(",", " ").split():
        resolution = resolve_entity(token.strip("?.!()"))
        if resolution.entities and not resolution.ambiguous:
            for entity in resolution.entities:
                if entity.canonical_id not in {item.canonical_id for item in entities}:
                    entities.append(entity)
    return entities


def _has_valid_workflow_continuation(ctx: FinancialContext) -> bool:
    if ctx.active_workflow is None:
        return False
    if not ctx.message.strip() or route_signals(ctx.message):
        return False
    return len(ctx.message.strip()) <= 80


class FinancialRouter:
    def __init__(self, semantic_router: SemanticRouter | None = None, llm_router: LLMRouter | None = None):
        self.semantic_router = semantic_router
        self.llm_router = llm_router
        validate_capability_registry()

    async def route(self, ctx: FinancialContext) -> ExecutionPlan:
        entities = _extract_entities(ctx)

        if _has_valid_workflow_continuation(ctx):
            capabilities = ctx.current_capabilities or [Capability.KNOWLEDGE]
            return self.build_plan(capabilities, ctx, entities=entities)

        signals = route_signals(ctx.message)
        if signals:
            capabilities = [signal.capability for signal in signals]
            freshness = next((signal.freshness for signal in signals if signal.freshness), Freshness.STATIC)
            return self.build_plan(capabilities, ctx, entities=entities, freshness=freshness)

        if self.semantic_router is not None:
            candidate = await self.semantic_router(ctx)
            if candidate is not None and candidate.confidence >= 0.85:
                return self.build_plan([candidate.capability], ctx, entities=entities)

        if self.llm_router is not None:
            decision = await self.llm_router(ctx)
            if decision is not None and decision.capabilities:
                return self.build_plan(
                    decision.capabilities,
                    ctx,
                    entities=decision.entities or entities,
                    freshness=decision.freshness,
                )

        return build_clarification_plan(ctx.message)

    async def route_line_request(self, ctx: FinancialContext, *, is_one_to_one: bool = False):
        """Preserve fixed LINE commands before routing unmatched text."""

        # legacy_response = parse_line_command(ctx.message, is_one_to_one)
        # print(legacy_response)
        # if legacy_response:
        #     return legacy_response
        return await self.route(ctx)

    def build_plan(
        self,
        capabilities: list[Capability],
        ctx: FinancialContext,
        *,
        entities: list[EntityReference] | None = None,
        freshness: Freshness = Freshness.STATIC,
    ) -> ExecutionPlan:
        tools, model_tier = build_capability_requirements(capabilities)
        return ExecutionPlan(
            capabilities=capabilities,
            entities=entities or [],
            freshness=freshness,
            tools=tools,
            workflow=ctx.active_workflow if _has_valid_workflow_continuation(ctx) else None,
            model_tier=model_tier,
        )
