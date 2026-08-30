## Purpose

Defines the supported finance-only analysis surface and its expected behavior across knowledge, markets, issuers, securities, portfolios, dividends, bonds, news, and research.

## ADDED Requirements

### Requirement: Support the complete capability taxonomy
The system SHALL support knowledge, market data, company analysis, security analysis, security comparison, portfolio analysis, dividend analysis, bond analysis, financial news, and web research, with clarification available when required inputs or tools are unavailable.

#### Scenario: Capability-specific request
- **WHEN** a user asks for a bond's terms and risk
- **THEN** the system selects bond analysis and obtains the required bond and issuer data before answering

### Requirement: Distinguish issuer and security analysis
Company analysis SHALL address issuers and companies; security analysis SHALL address a specific financial security; a request MAY select both.

#### Scenario: Issuer and security request
- **WHEN** a user compares a company's dividend capacity with a preferred share's yield
- **THEN** the plan includes company analysis and security analysis

### Requirement: Distinguish news from web research
Financial news SHALL cover recent events and announcements; web research SHALL cover cross-source background or non-standard financial information.

#### Scenario: Recent announcement
- **WHEN** a user asks what caused a company's recent price movement
- **THEN** the request uses financial news and does not require unrestricted web research by default

### Requirement: Cite changing data in answers
Answers based on recent or realtime information SHALL identify their sources and effective times and SHALL identify conflicting sources when they disagree.

#### Scenario: Conflicting sources
- **WHEN** two sources report different values for the same recent metric
- **THEN** the answer reports the discrepancy instead of silently selecting one value
