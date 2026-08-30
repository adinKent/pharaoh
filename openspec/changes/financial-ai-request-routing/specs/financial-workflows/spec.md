## Purpose

Provides resumable, explicit state for multi-step financial tasks while preventing stale workflows from hijacking unrelated user requests.

## ADDED Requirements

### Requirement: Persist workflow state
Each workflow SHALL persist its type, state, current step, collected inputs, pending question, timestamps, and expiry.

#### Scenario: Continue a workflow
- **WHEN** a user supplies the requested investment horizon
- **THEN** the portfolio workflow stores the value and advances to its next defined step

### Requirement: Support workflow lifecycle states
Workflows SHALL support active, suspended, completed, cancelled, and expired states.

#### Scenario: Expired workflow
- **WHEN** a user replies after the workflow expiry time
- **THEN** the system does not silently apply the old workflow state and asks whether to restart it

### Requirement: Suspend on topic change
The system SHALL preserve a workflow as suspended when a user makes a clear unrelated request and SHALL allow later resumption without losing collected inputs.

#### Scenario: Resume after interruption
- **WHEN** a user asks for a quote during portfolio construction and later returns to the portfolio
- **THEN** the quote is answered independently and the portfolio workflow resumes from its prior step
