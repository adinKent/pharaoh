## 1. Contracts and compatibility foundation

- [x] 1.1 Add typed models for `FinancialContext`, `EntityReference`, route decisions, execution requirements, workflow state, and execution plans; verify model validation tests cover valid and invalid payloads.
- [x] 1.2 Add the shared financial tool-result envelope with source, retrieval time, effective time, quality, stale status, and error fields; verify serialization tests.
- [x] 1.3 Inventory existing fixed LINE commands and existing LLM/data helpers; verify the inventory against `src/app.py`, `src/line/`, and `src/utils/`.
- [x] 1.4 Add a feature flag for unmatched natural-language routing and verify disabling it preserves current behavior.

## 2. Entity resolution and routing

- [x] 2.1 Implement market-aware entity resolution for issuers, securities, indices, currencies, and funds; verify canonical and ambiguous symbol tests.
- [x] 2.2 Implement clarification plans for unresolved or ambiguous entities; verify no financial tool is called when required entities are unresolved.
- [x] 2.3 Implement deterministic routing signals for explicit freshness, comparison, dividend, bond, portfolio, and news language; verify multilingual and overlapping-keyword tests.
- [x] 2.4 Implement semantic classification and structured LLM fallback behind provider-neutral interfaces; verify low-confidence fallback tests and malformed-output handling.
- [x] 2.5 Implement the unified decision builder and routing precedence for fixed commands, valid workflow continuation, topic override, rules, semantic classification, and LLM fallback; verify precedence tests.

## 3. Planner and capability registry

- [x] 3.1 Register the complete capability taxonomy and define entity requirements, freshness defaults, model tier, fallback behavior, and required tools for every capability; verify registry completeness tests.
- [x] 3.2 Implement execution-graph planning with dependency edges, critical/optional inputs, and duplicate tool-request deduplication; verify graph construction tests for single and multi-capability requests.
- [x] 3.3 Implement deployment-configured model tiers (`cheap`, `medium`, `strong`) without provider names in routing code; verify configuration mapping tests.
- [x] 3.4 Implement tool adapters for market data, financial statements, financial news, web research, bond data, portfolio calculations, and knowledge retrieval; verify each adapter returns the shared result envelope.

## 4. Freshness and answer generation

- [x] 4.1 Implement static, recent, and realtime freshness validation, including the five-minute market-hours rule and last-transaction behavior outside market hours; verify boundary-time tests.
- [x] 4.2 Implement source fallback, conflict detection, stale-data marking, and critical-data failure handling; verify the answer cannot present stale or invented values as current.
- [x] 4.3 Implement answer generation that cites sources/effective times for recent and realtime data and preserves calculation inputs; verify citation and conflicting-source tests.
- [x] 4.4 Implement `SAFETY_MODE=off|on` as deployment-scoped configuration and verify both modes are observable and covered by portfolio/buy-sell tests.

## 5. Workflow state and context

- [x] 5.1 Implement bounded conversation context separated into transcript, entity memory, and workflow state; verify user/group isolation and retention behavior.
- [x] 5.2 Implement workflow lifecycle transitions for active, suspended, completed, cancelled, and expired states; verify state-machine transition tests.
- [x] 5.3 Implement portfolio, company research, security comparison, and bond evaluation workflow handlers; verify continuation, topic suspension, resume, cancellation, and expiry scenarios.

## 6. LINE integration and asynchronous execution

- [x] 6.1 Integrate unmatched natural-language requests into the existing webhook without changing fixed-command behavior; verify the existing LINE test suite and new fallthrough tests.
- [x] 6.2 Implement synchronous execution for requests within the webhook budget; verify simple knowledge and market-data request responses.
- [x] 6.3 Implement durable asynchronous execution for long multi-tool requests with acknowledgment, status, retry classification, correlation ID, and LINE push delivery; verify end-to-end long-request tests.
- [x] 6.4 Implement event-derived idempotency and duplicate-delivery protection; verify repeated webhook events produce at most one final response.

## 7. Observability and evaluation

- [x] 7.1 Add structured routing, plan, tool, model, latency, token, data-quality, error, and safety-mode diagnostics; verify required fields are emitted for every route.
- [x] 7.2 Add default redaction for raw messages and sensitive identifiers plus an explicit temporary debug switch; verify normal logs contain no unredacted request content.
- [x] 7.3 Create the anonymized, versioned evaluation set covering every capability, multilingual cases, ambiguity, follow-ups, topic switches, fixed-command overlap, stale data, unavailable tools, duplicate delivery, and clarification; verify the dataset is runnable in CI or a documented evaluation command.
- [x] 7.4 Add acceptance checks for routing accuracy, realtime source/timestamp coverage, static-tool avoidance, clarification correctness, latency, cost, and deterministic failure behavior; verify the checks fail on intentionally invalid fixtures.

## 8. Migration and release validation

- [ ] 8.1 Deploy the new pipeline behind the feature flag while preserving the existing parser path; verify rollback by disabling the flag.
- [x] 8.2 Run compatibility, unit, integration, and routing evaluation suites against the full capability taxonomy; verify configured acceptance thresholds pass.
- [ ] 8.3 Enable natural-language routing for the intended LINE contexts and document operational configuration, data-source limitations, safety mode, and rollback procedure; verify the release checklist is complete.
