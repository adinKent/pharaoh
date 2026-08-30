import re
from dataclasses import dataclass

from line.command_mappings import get_all_commands
from routing.models import EntityKind, EntityReference


@dataclass(frozen=True)
class EntityResolution:
    """The result of resolving user text to zero or more canonical entities."""

    entities: tuple[EntityReference, ...]
    ambiguous: bool = False


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
