# Represent workflows as explicit state machines

Multi-step financial workflows will persist explicit state, current step, collected inputs, pending question, timestamps, and expiry rather than only an active workflow name. Workflows can be continued, suspended by a new topic, cancelled, completed, or expired. This makes follow-up routing deterministic and prevents stale state from silently controlling unrelated requests.
