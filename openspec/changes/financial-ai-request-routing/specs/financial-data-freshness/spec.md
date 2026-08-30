## Purpose

Makes the recency, provenance, quality, and failure state of financial information explicit so answers cannot silently present stale data as current.

## ADDED Requirements

### Requirement: Classify freshness
The system SHALL classify data needs as `static`, `recent`, or `realtime` before answer generation.

#### Scenario: Static definition
- **WHEN** the user asks what a P/E ratio means
- **THEN** the request is classified as static and changing market data is not required

#### Scenario: Realtime quote
- **WHEN** the user asks for a current market price
- **THEN** the request is classified as realtime and requires a timestamped market-data result

### Requirement: Expose data provenance
Every external financial result SHALL include source, retrieval time, effective time, quality, stale status, and error information.

#### Scenario: Timestamped result
- **WHEN** a market-data tool returns a quote
- **THEN** the answer can identify the source and the quote's effective time

### Requirement: Enforce freshness limits
During market hours, realtime quote data SHALL be no more than five minutes old; outside market hours, the system SHALL show the last transaction time.

#### Scenario: Stale realtime result
- **WHEN** the only available quote exceeds the realtime limit
- **THEN** the system marks it stale and does not present it as a current quote

### Requirement: Handle missing critical data
The system SHALL disclose missing critical data and SHALL NOT invent replacement financial values.

#### Scenario: Failed primary source
- **WHEN** a required financial statement source fails and no valid fallback exists
- **THEN** the answer states that a reliable conclusion cannot be made and identifies the missing data
