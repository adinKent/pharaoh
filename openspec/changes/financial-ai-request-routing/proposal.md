## Why

The current LINE bot primarily parses fixed commands and has limited natural-language inference, making it difficult to select the right financial data, preserve follow-up context, or extend analysis capabilities safely. This change introduces a finance-specific routing and execution contract so every supported request can select the required capability, entity, freshness, tools, workflow, and model behavior.

## What Changes

- Add a typed financial request context and canonical entity resolution boundary.
- Route requests across the complete financial capability taxonomy, including clarification for ambiguous or unsupported requests.
- Preserve existing fixed LINE commands as a compatibility layer and route unmatched natural-language requests through the new pipeline.
- Separate routing, planning, execution, and answer generation.
- Make freshness, source provenance, data quality, and calculation inputs explicit in tool results.
- Represent multi-tool work as an execution graph with deduplication, dependencies, partial-failure handling, and asynchronous processing for long requests.
- Persist explicit workflow state for multi-step portfolio, company research, security comparison, and bond evaluation flows.
- Add deployment-scoped `SAFETY_MODE` configuration, defaulting to `off` for the private deployment.
- Add structured, privacy-aware routing observability and a versioned evaluation set covering all capabilities.

## Capabilities

### New Capabilities

- `financial-request-routing`: Classifies finance requests, resolves entities, handles clarification, and produces validated execution plans.
- `financial-data-freshness`: Enforces static, recent, and realtime data requirements with source and timestamp visibility.
- `financial-analysis-capabilities`: Supports knowledge, market data, company analysis, security analysis, security comparison, portfolio analysis, dividend analysis, bond analysis, financial news, and web research.
- `financial-workflows`: Manages explicit stateful workflows, topic suspension, resumption, cancellation, completion, and expiry.
- `line-financial-request-execution`: Integrates routing with the existing LINE command parser and supports synchronous simple requests plus asynchronous multi-tool analysis.
- `routing-observability-and-evaluation`: Records routing diagnostics safely and validates routing behavior against a versioned case set.

### Modified Capabilities

- None. No existing OpenSpec capabilities are currently defined in this repository.

## Impact

- Affected entry point: `src/app.py` and the existing LINE command parser under `src/line/`.
- Affected LLM integrations: existing helpers under `src/utils/`, which must remain behind a provider-neutral model interface.
- Affected financial data modules: existing quote/search modules and new tool interfaces for statements, news, bonds, and portfolio calculations.
- New routing, planning, execution, workflow, context, and evaluation modules will be added incrementally.
- LINE webhook behavior must remain compatible for existing fixed commands, while long-running analysis may use background processing and LINE push messages.
