## Context

The current implementation is centered on `src/app.py`, `src/line/command_parser.py`, existing quote/search modules, and provider-specific LLM helpers under `src/utils/`. Existing fixed commands and their one-to-one/group behavior must remain compatible. See `proposal.md` and the capability specs for the required external behavior.

## Goals / Non-Goals

**Goals:**

- Add a provider-neutral routing boundary without coupling the LINE webhook to capabilities or tools.
- Resolve canonical financial entities before planning.
- Produce validated execution graphs with freshness and provenance requirements.
- Support all declared capabilities, while allowing their internal delivery to be staged.
- Preserve existing commands and provide reliable synchronous/asynchronous LINE response paths.
- Make routing quality, latency, data quality, and policy mode measurable.

**Non-Goals:**

- Replacing the existing fixed-command parser in this change.
- Creating one autonomous agent per capability.
- Adding per-user or per-request safety policy overrides.
- Treating a capability as supported without the required tools, fallback, and evaluation coverage.

## Decisions

### Keep a compatibility-first entry boundary

The webhook continues to pass fixed commands through the existing parser. Only unmatched natural-language requests enter the new pipeline. This minimizes regression risk and preserves group-message behavior. Replacing the parser first was rejected because it would combine routing migration with existing command behavior changes.

### Use explicit typed boundaries

The pipeline uses typed models for request context, entity references, route decisions, execution requirements, workflow state, tool results, and execution graph nodes. The Router emits capability and requirement signals; the Planner owns tool selection and dependency construction. A flat router-to-tool map was rejected because it cannot express multi-capability dependencies or partial failure.

### Separate entity resolution from capability routing

An Entity Resolver maps aliases and symbols to market-aware canonical IDs. It returns clarification for ambiguity. Letting the LLM Router resolve identities was rejected because identity errors are more dangerous and harder to observe than capability classification errors.

### Use staged routing with a single decision builder

The decision path is: explicit fixed command, valid workflow continuation/topic override, deterministic signals, semantic classification, then structured LLM fallback. All paths converge on one builder that validates entities, freshness, capabilities, and plan requirements. This avoids rule and model paths producing incompatible plans.

### Build an execution graph

The Planner creates nodes for retrieval, calculation, analysis, and answer generation, with declared inputs and dependencies. Independent retrieval runs may be parallelized and duplicate requests deduplicated. Critical versus optional inputs are explicit so the answer can report partial results safely.

### Use shared data-result metadata

All external data adapters normalize results into a common envelope containing data, source, retrieved time, effective time, quality, stale status, and error. Freshness validation happens before answer generation; the model cannot silently downgrade a requirement.

### Use deployment-level policy and model configuration

`SAFETY_MODE` and model-tier mappings are deployment configuration. The private deployment defaults safety mode to `off`; model tiers describe latency/cost/reasoning requirements rather than vendor names. Per-user policy was rejected as unnecessary initial complexity.

### Introduce asynchronous processing only for long work

Requests within the webhook budget remain synchronous. Multi-tool work uses durable request state, idempotency, retries, correlation IDs, and LINE push delivery. Making every request asynchronous was rejected because it would add latency and operational complexity to simple quote and knowledge requests.

## Risks / Trade-offs

- [Full capability scope increases delivery size] → Require a contract, fallback, tool coverage, and evaluation cases for every capability; stage internal implementation without declaring incomplete behavior supported.
- [Entity aliases may be incomplete or ambiguous] → Maintain market-aware canonical mappings and route unresolved cases to clarification.
- [External sources may be stale or disagree] → Preserve provenance and effective times, validate freshness, and disclose conflicts.
- [Background work may be duplicated by webhook retries] → Use LINE event-derived idempotency and durable request status.
- [Routing logs may expose financial preferences] → Redact raw messages and identifiers by default; gate temporary raw logging behind an explicit debug setting.
- [Existing command behavior may regress] → Keep the parser as the first compatibility boundary and retain its unit/integration tests.

## Migration Plan

1. Add typed models, tool-result envelope, and capability configuration without changing the webhook.
2. Add entity resolution and the unified decision builder behind a feature flag.
3. Delegate unmatched one-to-one natural-language requests to the new synchronous pipeline.
4. Add capability-specific adapters and evaluation cases across the full taxonomy.
5. Add persisted workflow state and asynchronous execution for requests exceeding the synchronous budget.
6. Enable broader natural-language contexts only after compatibility and routing evaluation thresholds pass.

Rollback disables the new-routing feature flag and returns unmatched requests to the existing behavior; fixed commands remain unchanged throughout the migration.
