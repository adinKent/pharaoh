# Support the full capability taxonomy from the first implementation

The first implementation will support the complete financial capability taxonomy rather than limiting the MVP to knowledge, market data, and company analysis. Delivery may still be staged internally, but every declared capability must have an explicit route, planner behavior, tool contract, fallback, and acceptance cases before it is considered supported.

## Consequences

- The initial scope is broader and requires capability-specific test fixtures.
- Unsupported behavior must route to `clarification` rather than silently appearing implemented.
- Capability support does not require a separate autonomous agent for each capability.
