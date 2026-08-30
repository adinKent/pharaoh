# Preserve the existing LINE command flow during migration

The existing fixed-command parser remains the compatibility layer for commands such as `#2330`, `A2330`, `P2330`, and `D除息`. The new Financial Router handles unmatched natural-language requests, initially behind a feature flag. This incremental boundary preserves current behavior, including the existing distinction between one-to-one and group messages, while allowing the routing architecture to be introduced safely.

## Consequences

- The webhook handler must keep the old parser boundary stable while delegating only unmatched requests.
- New routing tests must cover both fixed commands and natural-language fallthrough.
- Removing or replacing the compatibility layer is a later migration decision.
