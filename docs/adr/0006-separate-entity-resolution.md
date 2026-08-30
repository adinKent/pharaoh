# Resolve financial entities before routing

Entity resolution will be a distinct boundary before capability routing. User-provided names, symbols, aliases, and market hints are mapped to canonical entity references; ambiguous references require clarification and are never guessed by the Router or Answer Generator. This separates identity errors from capability errors and protects downstream financial tools from receiving unresolved ticker strings.

## Consequences

- Entity references must distinguish issuer, security, index, currency, and fund.
- Routing can proceed only when required entities are resolved or the plan explicitly requests clarification.
- The resolver needs market-aware aliases and an auditable confidence result.
