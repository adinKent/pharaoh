import asyncio
import json
import logging

from routing.entities import resolve_entity
from routing.models import FinancialContext, RouteDecision

logger = logging.getLogger(__name__)

CAPABILITY_ALIASES = {
    "sector_performance_analysis": "market_data",
    "news_search": "financial_news",
    "market_analysis": "market_data",
    "instrument_analysis": "security_analysis",
}


def _parse_json(content: str) -> dict:
    text = (content or "{}").strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("\n", 1)[0]
    value = json.loads(text)
    if not isinstance(value, dict):
        raise ValueError("LLM router response must be a JSON object")
    return value


def _normalize_capability_aliases(payload: dict) -> dict:
    """Normalize known model vocabulary while preserving strict enum validation."""
    capabilities = payload.get("capabilities")
    if isinstance(capabilities, list):
        payload = {**payload, "capabilities": [CAPABILITY_ALIASES.get(value, value) for value in capabilities]}
    return payload


def _normalize_entities(payload: dict) -> dict:
    entities = payload.get("entities")
    if not isinstance(entities, list):
        return payload
    normalized = []
    for entity in entities:
        if isinstance(entity, str):
            resolution = resolve_entity(entity)
            if len(resolution.entities) == 1 and not resolution.ambiguous:
                normalized.append(resolution.entities[0].model_dump(mode="json"))
            else:
                normalized.append(entity)
        else:
            normalized.append(entity)
    return {**payload, "entities": normalized}


async def llm_route(ctx: FinancialContext, *, client=None) -> RouteDecision | None:
    """Use an OpenAI-compatible client only after deterministic routing is uncertain."""
    if client is None:
        from utils.openai_helper import fallback_models, get_openai_client, main_model

        client = get_openai_client()
    else:
        from utils.openai_helper import fallback_models, main_model

    prompt = (
        "Classify this finance-only request. Return JSON only with keys: "
        "capabilities (array), confidence (0..1), freshness (static|recent|realtime), "
        "requires_market_data, requires_news_search, requires_financial_statements. "
        "Capabilities MUST use only these values: knowledge, market_data, company_analysis, "
        "security_analysis, security_comparison, portfolio_analysis, dividend_analysis, "
        "bond_analysis, financial_news, web_research, clarification. "
        "entities MUST be an array of resolved objects with kind, canonical_id, symbol, market, display_name, and confidence; "
        "Use clarification if the request is ambiguous or unsupported.\n"
        f"Request: {ctx.message}\n"
        f"Known entities: {[entity.canonical_id for entity in ctx.known_entities]}"
    )

    try:
        for model in (main_model, *fallback_models):
            try:
                response = await asyncio.to_thread(
                    client.chat.completions.create,
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                )
                payload = _normalize_entities(_normalize_capability_aliases(_parse_json(response.choices[0].message.content)))
                return RouteDecision.model_validate(payload)
            except Exception as error:
                logger.warning("LLM financial routing failed with %s: %s", model, error)
        return None
    except Exception as error:
        logger.warning("LLM financial routing failed: %s", error)
        return None
