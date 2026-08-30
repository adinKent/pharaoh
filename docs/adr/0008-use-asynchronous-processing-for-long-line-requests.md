# Use asynchronous processing for long LINE requests

Simple requests may be answered synchronously, but multi-tool financial analysis will use asynchronous processing: acknowledge the webhook quickly, execute the work in the background, and send the completed answer through a LINE push message. A correlation ID will connect the webhook, routing decision, tool calls, and final response. This protects webhook responsiveness while allowing richer analysis workflows.

## Consequences

- The system needs durable request status and retry behavior.
- Users need an explicit waiting or failure message.
- Tests must cover duplicate delivery and out-of-order completion.
