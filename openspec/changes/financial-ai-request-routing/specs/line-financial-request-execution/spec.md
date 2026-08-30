## Purpose

Integrates the new financial routing pipeline with the existing LINE webhook while preserving fixed-command compatibility and reliable delivery for long-running analysis.

## ADDED Requirements

### Requirement: Preserve webhook compatibility
Existing fixed commands SHALL retain their current LINE response behavior, including the existing one-to-one and group-message distinctions.

#### Scenario: Group message fixed-command behavior
- **WHEN** a group message does not meet the existing command inference conditions
- **THEN** the system preserves the current non-response behavior unless the new flow is explicitly enabled for that context

### Requirement: Process simple requests synchronously
Simple requests that complete within the webhook response budget SHALL return a direct LINE response.

#### Scenario: Simple market request
- **WHEN** a market-data request completes within the response budget
- **THEN** the user receives the answer synchronously

### Requirement: Process long requests asynchronously
Multi-tool requests exceeding the synchronous budget SHALL receive a prompt acknowledgment and later a LINE push message containing the result or failure state.

#### Scenario: Long analysis
- **WHEN** a security comparison requires multiple external tools
- **THEN** the webhook acknowledges promptly and the completed result is delivered asynchronously

### Requirement: Prevent duplicate delivery
The system SHALL use an idempotency key to prevent duplicate webhook delivery from producing duplicate final responses.

#### Scenario: Duplicate event
- **WHEN** the same LINE event is delivered more than once
- **THEN** the system processes it once or returns the existing result without sending a duplicate answer
