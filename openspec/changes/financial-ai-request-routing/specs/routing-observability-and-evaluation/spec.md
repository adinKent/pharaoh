## Purpose

Makes routing decisions measurable and debuggable while limiting sensitive message exposure and protecting regressions across the complete capability taxonomy.

## ADDED Requirements

### Requirement: Record routing diagnostics
The system SHALL record route, confidence, resolved entities, freshness, selected tools, model tier, latency, token usage, data quality, and errors for every routed request.

#### Scenario: Routed request log
- **WHEN** a natural-language request receives an execution plan
- **THEN** the diagnostic record contains the plan's routing and execution metadata

### Requirement: Protect raw user content
The system SHALL redact raw messages and sensitive identifiers from normal logs and SHALL require an explicit debug switch for temporary raw-payload logging.

#### Scenario: Normal production logging
- **WHEN** a request contains free text or financial preferences
- **THEN** normal routing logs contain diagnostics without the unredacted message

### Requirement: Evaluate every capability
The system SHALL evaluate routing against a versioned, anonymized case set covering every declared capability, multilingual requests, ambiguous entities, follow-ups, topic changes, fixed-command overlap, stale data, unavailable tools, duplicate delivery, and clarification.

#### Scenario: Routing regression
- **WHEN** a capability rule or model changes
- **THEN** the evaluation set is rerun and the results are available before the change is accepted

### Requirement: Make safety mode observable
The system SHALL record the active deployment-scoped safety mode and SHALL support both `SAFETY_MODE=off` and `SAFETY_MODE=on` in evaluation cases.

#### Scenario: Private deployment
- **WHEN** the private deployment uses `SAFETY_MODE=off`
- **THEN** the active mode is observable and the configured private-use behavior is applied
