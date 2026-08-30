# Capability-based financial request routing

The chatbot will route requests by the financial capability required to answer them, rather than by broad intent or autonomous-agent identity. Capabilities may be combined; workflows represent stateful multi-step interactions and can be suspended by a new topic. This keeps the system aligned with its finance-only scope while allowing centralized planning, data freshness enforcement, and future capability expansion without coupling the LINE webhook to individual tools.

## Consequences

- Capability names and boundaries become part of the domain contract.
- Entity references must distinguish issuers from securities and represent ambiguity explicitly.
- The planner, rather than the answer model, enforces freshness and tool requirements.
