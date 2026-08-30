## Purpose

Provides a deterministic, finance-specific boundary that turns LINE requests into validated capability, entity, freshness, and execution decisions.

## ADDED Requirements

### Requirement: Route requests by financial capability
The system SHALL classify each supported request into one or more declared financial capabilities and SHALL use `clarification` when the request is ambiguous or unsupported.

#### Scenario: Multi-capability analysis
- **WHEN** a user asks whether a recent dividend change is sustainable
- **THEN** the route includes dividend analysis, company analysis, and the data capabilities required to support the answer

### Requirement: Resolve entities before execution
The system SHALL resolve referenced issuers, securities, indices, currencies, and funds to canonical entity references before planning tool execution.

#### Scenario: Ambiguous security reference
- **WHEN** a symbol maps to multiple markets or securities
- **THEN** the system asks for clarification and does not execute a financial tool with the unresolved symbol

### Requirement: Preserve existing fixed commands
The system SHALL continue handling existing fixed LINE commands through the compatibility layer before delegating unmatched natural-language requests to the new router.

#### Scenario: Existing quote command
- **WHEN** the user sends `#2330`
- **THEN** the existing fixed-command behavior is preserved and the new natural-language route is not required

### Requirement: Respect topic changes during workflows
The system SHALL continue a workflow only when the message is a valid next step; an explicit command or clear topic change SHALL suspend the workflow.

#### Scenario: Topic change during portfolio workflow
- **WHEN** a user building a portfolio asks for a current stock price
- **THEN** the price request is routed independently and the portfolio workflow is retained as suspended state
