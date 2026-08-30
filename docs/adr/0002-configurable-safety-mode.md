# Configurable safety mode for personal use

Because the initial chatbot is for private personal use, safety restrictions such as investment-advice disclaimers and refusal behavior will not be mandatory by default. The system will expose a deployment-level configuration switch for enabling these safeguards when the audience or deployment context changes, so the policy boundary can evolve without redesigning request routing.

## Consequences

- The active safety mode must be observable and testable.
- Portfolio and buy/sell capabilities must still have explicit behavior under both modes.
- Enabling the mode later is a policy/configuration change, not a routing taxonomy change.
- Per-user and per-request policy overrides are intentionally deferred.
- The initial deployment uses `SAFETY_MODE=off`; changing the deployment to a broader audience requires explicitly enabling the mode.
