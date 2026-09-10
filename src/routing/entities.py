import re
from dataclasses import dataclass

from line.command_mappings import get_all_commands
from routing.models import EntityKind, EntityReference


@dataclass(frozen=True)
class EntityResolution:
    """The result of resolving user text to zero or more canonical entities."""

    entities: tuple[EntityReference, ...]
    ambiguous: bool = False


KNOWN_TW_ISSUERS = {
    "台積電": ("2330", "台積電"),
    "國泰金": ("2882", "國泰金控"),
    "長榮": ("2603", "長榮"),
}


def _reference(symbol: str, market: str, kind: EntityKind = EntityKind.SECURITY, display_name: str | None = None) -> EntityReference:
    normalized_market = market.upper()
    return EntityReference(
        kind=kind,
        canonical_id=f"{normalized_market}:{symbol.upper()}",
        symbol=symbol.upper(),
        market=normalized_market,
        display_name=display_name or symbol.upper(),
        confidence=1.0,
    )


def resolve_entity(text: str) -> EntityResolution:
    """Resolve a single user-provided symbol or known fixed alias."""
    value = re.sub(r"\s+", "", (text or "").strip())
    if not value:
        return EntityResolution(())

    if value in {"台股", "台灣股市", "台股大盤"}:
        return EntityResolution((_reference("IX0001", "TW", EntityKind.INDEX, "台股大盤"),))

    issuer = KNOWN_TW_ISSUERS.get(value)
    if issuer:
        symbol, display_name = issuer
        return EntityResolution((_reference(symbol, "TW", EntityKind.ISSUER, display_name),))

    fixed = get_all_commands().get(value)
    if fixed is not None:
        values = fixed if isinstance(fixed, list) else [fixed]
        refs = tuple(
            _reference(
                symbol,
                "TW" if market.startswith("TW") else "US",
                EntityKind.INDEX if market in {"TW_IND", "IND"} else EntityKind.SECURITY,
                value,
            )
            for symbol, market in values
        )
        return EntityResolution(refs, ambiguous=len(refs) > 1)

    if value[0].isdigit():
        return EntityResolution((_reference(value, "TW"),))

    if re.fullmatch(r"\^?[A-Za-z0-9][A-Za-z0-9.=_-]*", value):
        kind = EntityKind.INDEX if value.startswith("^") else EntityKind.SECURITY
        return EntityResolution((_reference(value, "US", kind),))

    return EntityResolution(())


def resolve_entities_in_text(text: str) -> tuple[EntityReference, ...]:
    """Resolve known Chinese aliases and token-like symbols from a message."""
    value = text or ""
    candidates = [alias for alias in KNOWN_TW_ISSUERS if alias in value]
    candidates.extend(alias for alias in ("台股", "台灣股市", "台股大盤") if alias in value)
    candidates.extend(value.replace(",", " ").split())
    resolved: list[EntityReference] = []
    for candidate in candidates:
        result = resolve_entity(candidate.strip("?.!()"))
        if result.entities and not result.ambiguous:
            for entity in result.entities:
                if entity.canonical_id not in {item.canonical_id for item in resolved}:
                    resolved.append(entity)
    return tuple(resolved)
