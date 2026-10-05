# Graph Report - pharaoh  (2026-10-05)

## Corpus Check
- 118 files · ~48,247 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 910 nodes · 1516 edges · 79 communities (63 shown, 16 thin omitted)
- Extraction: 77% EXTRACTED · 23% INFERRED · 0% AMBIGUOUS · INFERRED: 356 edges (avg confidence: 0.76)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `955e3db1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Command Parser & Mappings
- Chart Rendering
- Taiwan Stock Data
- LINE Webhook & Flex
- Fugle Quote Charts
- OpenCode Inference
- AWS & Broker Helpers
- Command Parser Tests
- OpenCode Helper Tests
- Fixed Command Tests
- Architecture Docs
- Serverless Infrastructure
- NVDA Yearly Chart
- Yahoo Finance Tests
- Image Design Guidelines
- NVDA Intraday Chart
- OHI Chart Data
- Dependencies
- Groq Helper Tests
- OpenCode Config
- CI & Environment
- Deploy Script
- Init Script
- Local Script
- opencode_helper.py
- Decisions
- ADDED Requirements
- ADDED Requirements
- ADDED Requirements
- ADDED Requirements
- ADDED Requirements
- ADDED Requirements
- tasks.md
- proposal.md
- command_parser.py
- get_tw_futopt_price
- TestFormatStockPriceResponse
- Financial AI Chatbot Context
- Capability-based financial request routing
- Configurable safety mode for personal use
- Planner produces an execution graph
- Preserve the existing LINE command flow during migration
- Standardize financial tool results
- Resolve financial entities before routing
- Use asynchronous processing for long LINE requests
- Support the full capability taxonomy from the first implementation
- Define capability and research boundaries
- financial_ai_request_routing_proposal.md
- 0007-explicit-workflow-state-machines.md
- 0009-version-routing-evaluation-set.md
- fugle.py
- models.py
- test_entities_and_rules.py
- FinancialContext
- output.py
- tw_stock.py
- TestApp
- get_ups_or_downs
- idempotency.py
- get_tw_stock_symbol_from_company_name
- LLMRouter
- handle_text_message
- SKILL.md
- chart_theme.py
- get_institues_buy_sell_today_result
- groq_helper.py
- ExecutionPlan
- TestQuoteStock
- Financial Request Routing Operational Guide & Release Checklist
- observability.py
- Financial routing inventory

## God Nodes (most connected - your core abstractions)
1. `parse_line_command()` - 33 edges
2. `FinancialContext` - 32 edges
3. `ExecutionPlan` - 28 edges
4. `TestParseLineCommand` - 24 edges
5. `handle_text_message()` - 23 edges
6. `EntityReference` - 21 edges
7. `ToolResult` - 20 edges
8. `get_tw_stock_price()` - 19 edges
9. `FinancialRouter` - 19 edges
10. `Capability` - 18 edges

## Surprising Connections (you probably didn't know these)
- `Development Requirements` --semantically_similar_to--> `Runtime Requirements`  [INFERRED] [semantically similar]
  requirements-dev.txt → src/requirements.txt
- `test_evaluation_set_covers_all_declared_capabilities()` --indirect_call--> `Capability`  [INFERRED]
  tests/unit/routing/test_observability_evaluation.py → src/routing/models.py
- `test_execution_plan_rejects_unknown_model_tier()` --calls--> `ExecutionPlan`  [INFERRED]
  tests/unit/routing/test_models.py → src/routing/models.py
- `test_rules_keep_overlapping_signals_instead_of_returning_one_capability()` --calls--> `route_signals()`  [INFERRED]
  tests/unit/routing/test_entities_and_rules.py → src/routing/rules.py
- `test_rules_support_chinese_and_english_comparison()` --calls--> `route_signals()`  [INFERRED]
  tests/unit/routing/test_entities_and_rules.py → src/routing/rules.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Chart Design Pillars** — _claude_skills_image_response_design_skill_color_tokens, _claude_skills_image_response_design_skill_tw_polarity, _claude_skills_image_response_design_skill_palette_validation, _claude_skills_image_response_design_skill_intraday_layout [EXTRACTED 1.00]

## Communities (79 total, 16 thin omitted)

### Community 0 - "Command Parser & Mappings"
Cohesion: 0.09
Nodes (16): parse_line_command(), If text starts with '#', extract the symbol and return it with market type., Test cases for parse_line_command function, Test getting Taiwan stock info, Test getting US stock info, A partial Yahoo row must not make every moving average NaN., NaN moving averages (too little history) must not be written into the output., Test non-stock commands return None (+8 more)

### Community 1 - "Chart Rendering"
Cohesion: 0.14
Nodes (12): aggregate_dividend_records(), fetch_dividends_yfinance(), fetch_tw_stock_dividends_finmind(), generate_dividend_chart_png(), Aggregate records: past 5 years into annual sums, current year into individual p, Fetch dividend data, aggregate records, render stacked bar chart, and return ima, Fetch dividend policy history from FinMind API for Taiwan stocks., Fetch dividend history from yfinance as primary (US) or fallback (TW). (+4 more)

### Community 2 - "Taiwan Stock Data"
Cohesion: 0.07
Nodes (40): MongoClient, _extract_autocomplete_company_name(), format_total_net_diff(), _format_trade_value(), format_twse_buy_and_sell_result(), get_effective_date(), get_institues_buy_sell_today_result(), get_symbol_buy_sell_today_result() (+32 more)

### Community 3 - "LINE Webhook & Flex"
Cohesion: 0.05
Nodes (32): FlexMessage, MessagingApi, create_candidate_commands_flex(), handle_text_message(), mark_message_as_read(), Uses the Line SDK to send a reply message., Build clickable LINE commands so users can resolve ambiguous requests., Send a Flex Message reply through the LINE Messaging API. (+24 more)

### Community 4 - "Fugle Quote Charts"
Cohesion: 0.12
Nodes (10): _fallback_stock_price(), Fallback method using Taiwan Stock Exchange API or web scraping., Test fallback method when the fugle history fetch raises, Test fallback using TWSE API, Test cases for get_tw_stock_price function, Test successful stock price fetch using fugle (no period -> no history), With a period, history is fetched from Fugle and shaped like a yfinance frame., Test when fugle returns no data for the symbol (+2 more)

### Community 5 - "OpenCode Inference"
Cohesion: 0.08
Nodes (45): datetime, answer_data_status(), source_note(), Return the deployment-scoped safety mode., safety_mode(), choose_best_result(), conflicting_results(), missing_critical_data() (+37 more)

### Community 6 - "AWS & Broker Helpers"
Cohesion: 0.18
Nodes (16): get_x_label_align(), ChartTheme, get_chart_theme(), Color tokens for chart image responses.  Single source of truth for every color, Return the active theme. Selected via CHART_THEME env var; defaults to tradingvi, format_price_output(), get_info_for_day_candle_picture(), Get icon representation for ups or downs status (+8 more)

### Community 7 - "Command Parser Tests"
Cohesion: 0.15
Nodes (7): Test cases for get_stock_symbol_and_marke_type function, Test parsing valid stock symbols starting with #, Test parsing with leading/trailing spaces, Test various invalid formats, Test fixed commands like #大盤, #美股, etc., Test tw company commands like #台積電, #長榮, etc., TestGetStockSymbolAndMarketType

### Community 8 - "OpenCode Helper Tests"
Cohesion: 0.22
Nodes (7): format_stock_price_response(), Get icon representation for ups or downs status, Test cases for format_stock_price_response function, Test formatting when price is up, Test formatting when price is down, Test formatting when price is unchanged, TestFormatStockPriceResponse

### Community 10 - "Architecture Docs"
Cohesion: 0.17
Nodes (10): AWS SAM Container Lambdas, LINE Messaging API Bot, Pharaoh, Trust Code Over README Boilerplate, S3 Presigned URL Image Reply, AWS Lambda, AWS SAM, CloudWatch (+2 more)

### Community 11 - "Serverless Infrastructure"
Cohesion: 0.27
Nodes (10): llm_route(), _normalize_capability_aliases(), _normalize_entities(), _parse_json(), Normalize known model vocabulary while preserving strict enum validation., Use an OpenAI-compatible client only after deterministic routing is uncertain., test_llm_router_normalizes_known_capability_aliases(), test_llm_router_parses_structured_response_without_exposing_reasoning() (+2 more)

### Community 12 - "NVDA Yearly Chart"
Cohesion: 0.18
Nodes (11): NVDA 1-Year Candlestick Chart, Period High 236.26, Period Low 164.08, 20-Day MA 202.12, 5-Day MA 207.61, 60-Day MA 208.85, Current Price 202.81 (-2.21%), NVIDIA Corporation (NVDA) (+3 more)

### Community 13 - "Yahoo Finance Tests"
Cohesion: 0.36
Nodes (5): Figure, _build_candles_figure(), get_tw_stock_candles_png(), get_tw_stock_candles_png_bytes(), upload_tw_stock_candles_png_to_s3()

### Community 14 - "Image Design Guidelines"
Cohesion: 0.29
Nodes (8): Fixed MA Categorical Slots, Chart Color Tokens, dataviz skill (referenced), Image Response Design Guideline, Intraday P-Chart Layout & Scale, Palette Validation via validate_palette, Theme Discipline (Selected Not Flipped), Taiwan Market Polarity Convention

### Community 15 - "NVDA Intraday Chart"
Cohesion: 0.25
Nodes (8): NVDA Intraday Chart, Intraday High 206.65, Intraday Low 197.97, Price 202.81 (-4.59, -2.21%), US Session 09:30-16:00, yfinance data source, NVIDIA Corporation (NVDA), Turnover 126.8M

### Community 16 - "OHI Chart Data"
Cohesion: 0.29
Nodes (7): OHI Intraday Chart, Day High 50.75 / Low 49.71, Intraday Price 50.21 (+0.68%), Data source: yfinance (US intraday), Omega Healthcare Investors (OHI), Trend: morning peak, midday dip, late-day recovery, Trade Turnover 1.5M

### Community 17 - "Dependencies"
Cohesion: 0.33
Nodes (7): google-genai, Development Requirements, google-genai, line-bot-sdk, pymongo, Runtime Requirements, yfinance

### Community 19 - "Groq Helper Tests"
Cohesion: 0.47
Nodes (3): completion(), test_generate_response_retries_with_fallback_model(), test_generate_response_uses_main_model()

### Community 20 - "OpenCode Config"
Cohesion: 0.50
Nodes (3): instructions, $schema, ./claude/CLAUDE.md

### Community 27 - "opencode_helper.py"
Cohesion: 0.09
Nodes (33): OpenAI, get_all_commands(), get_command_catalog(), get_fixed_command_examples(), Return fixed aliases and their backend symbols for inference context., build_line_command_prompt(), _chat_with_tools(), generate_openai_technical_analysis_response() (+25 more)

### Community 28 - "Decisions"
Cohesion: 0.14
Nodes (13): Build an execution graph, Context, Decisions, Goals / Non-Goals, Introduce asynchronous processing only for long work, Keep a compatibility-first entry boundary, Migration Plan, Risks / Trade-offs (+5 more)

### Community 29 - "ADDED Requirements"
Cohesion: 0.17
Nodes (11): ADDED Requirements, Purpose, Requirement: Classify freshness, Requirement: Enforce freshness limits, Requirement: Expose data provenance, Requirement: Handle missing critical data, Scenario: Failed primary source, Scenario: Realtime quote (+3 more)

### Community 30 - "ADDED Requirements"
Cohesion: 0.18
Nodes (10): ADDED Requirements, Purpose, Requirement: Cite changing data in answers, Requirement: Distinguish issuer and security analysis, Requirement: Distinguish news from web research, Requirement: Support the complete capability taxonomy, Scenario: Capability-specific request, Scenario: Conflicting sources (+2 more)

### Community 31 - "ADDED Requirements"
Cohesion: 0.18
Nodes (10): ADDED Requirements, Purpose, Requirement: Preserve existing fixed commands, Requirement: Resolve entities before execution, Requirement: Respect topic changes during workflows, Requirement: Route requests by financial capability, Scenario: Ambiguous security reference, Scenario: Existing quote command (+2 more)

### Community 32 - "ADDED Requirements"
Cohesion: 0.18
Nodes (10): ADDED Requirements, Purpose, Requirement: Preserve webhook compatibility, Requirement: Prevent duplicate delivery, Requirement: Process long requests asynchronously, Requirement: Process simple requests synchronously, Scenario: Duplicate event, Scenario: Group message fixed-command behavior (+2 more)

### Community 33 - "ADDED Requirements"
Cohesion: 0.18
Nodes (10): ADDED Requirements, Purpose, Requirement: Evaluate every capability, Requirement: Make safety mode observable, Requirement: Protect raw user content, Requirement: Record routing diagnostics, Scenario: Normal production logging, Scenario: Private deployment (+2 more)

### Community 34 - "ADDED Requirements"
Cohesion: 0.22
Nodes (8): ADDED Requirements, Purpose, Requirement: Persist workflow state, Requirement: Support workflow lifecycle states, Requirement: Suspend on topic change, Scenario: Continue a workflow, Scenario: Expired workflow, Scenario: Resume after interruption

### Community 35 - "tasks.md"
Cohesion: 0.22
Nodes (8): 1. Contracts and compatibility foundation, 2. Entity resolution and routing, 3. Planner and capability registry, 4. Freshness and answer generation, 5. Workflow state and context, 6. LINE integration and asynchronous execution, 7. Observability and evaluation, 8. Migration and release validation

### Community 36 - "proposal.md"
Cohesion: 0.29
Nodes (6): Capabilities, Impact, Modified Capabilities, New Capabilities, What Changes, Why

### Community 37 - "command_parser.py"
Cohesion: 0.23
Nodes (15): format_symbol_buy_sell_response(), get_stock_symbol_and_market_type(), handle_buy_and_sell_quote(), handle_day_k_line(), handle_stock_basic_analysis_quote(), handle_stock_dividend_chart(), handle_stock_price_quote(), handle_year_k_line() (+7 more)

### Community 38 - "get_tw_futopt_price"
Cohesion: 0.14
Nodes (16): ContextStore, ConversationContext, InMemoryContextStore, MongoContextStore, BaseModel, Protocol, Persist context using the project's existing MongoDB configuration., Message (+8 more)

### Community 39 - "TestFormatStockPriceResponse"
Cohesion: 0.27
Nodes (6): completion(), test_generate_response_runs_tool_calls(), test_generate_response_uses_main_model(), test_infer_line_command_ignores_low_confidence(), test_infer_line_command_returns_high_confidence_candidate(), tool_call()

### Community 40 - "Financial AI Chatbot Context"
Cohesion: 0.40
Nodes (4): Data requirements, Financial AI Chatbot Context, Operating modes, Request routing

### Community 50 - "financial_ai_request_routing_proposal.md"
Cohesion: 0.05
Nodes (40): 10. Layer 4: Semantic Router, 11. Layer 5: LLM Router, 12. Freshness Routing, 13. Execution Plan, 14. Capability to Tool Mapping, 15. Model Routing, 16. Main Router Implementation, 17. Planner and Router Should Be Separate (+32 more)

### Community 53 - "fugle.py"
Cohesion: 0.18
Nodes (13): _get_api_key(), _get_api_key(), _get_api_secret(), get_futopt_snapshot(), Get a one-shot futures/options snapshot from SinoPac's shioaji API.     Returns, get_secret(), get_ssm_parameter(), Fetches a parameter from AWS SSM Parameter Store, using a cache. (+5 more)

### Community 54 - "models.py"
Cohesion: 0.16
Nodes (16): build_clarification_plan(), Build a plan that asks the user for missing information before tool use., EntityResolution, The result of resolving user text to zero or more canonical entities., Resolve a single user-provided symbol or known fixed alias., Resolve known Chinese aliases and token-like symbols from a message., _reference(), resolve_entities_in_text() (+8 more)

### Community 55 - "test_entities_and_rules.py"
Cohesion: 0.21
Nodes (7): get_stock_symbol_from_fixed_command(), Test #台指期 command maps to TXFR1 with TW_FUT market type, Test #台積期 command maps to CDFR1 with TW_FUT market type, Test unknown command should return None, Test cases for get_stock_symbol_from_fixed_command function, Test #美股 command returns list of US indices, TestGetStockSymbolFromFixedCommand

### Community 56 - "FinancialContext"
Cohesion: 0.22
Nodes (7): Command grammar (the bot's user interface), Commands, Config & secrets, graphify, Quote data sources, Tests, What this is

### Community 57 - "output.py"
Cohesion: 0.12
Nodes (13): handle_ex_dividend_quote(), format_analysis_output(), format_cash_dividend(), format_ex_dividend_response(), get_ups_or_downs(), Determine if the stock price is up, down, or unchanged.     Returns 1 for up, -1, Test cases for get_ups_or_downs function, Test when current price is higher than previous close (+5 more)

### Community 58 - "tw_stock.py"
Cohesion: 0.29
Nodes (4): get_tw_futopt_price(), Test get_tw_futopt_price returns formatted dict., Test get_tw_futopt_price returns None when snapshot fails., Test get_tw_futopt_price returns formatted dict for TSMC futures.

### Community 59 - "TestApp"
Cohesion: 0.13
Nodes (19): DataFrame, draw_turnover_header(), load_chart_font_name(), Shared chart-rendering helpers used by both the TW (Fugle) and US/foreign (yfina, Register the bundled Noto Sans TC font and return its family name., Render the top-right turnover block: label / number / unit columns, right-aligne, Save the figure locally (dev) or upload to S3 and return a presigned URL (Lambda, save_or_upload_fig() (+11 more)

### Community 60 - "get_ups_or_downs"
Cohesion: 0.16
Nodes (19): lambda_handler(), FinancialContext, _extract_entities(), FinancialRouter, _has_valid_workflow_continuation(), Resolve token-like symbols and retain already resolved conversation entities., Preserve fixed LINE commands before routing unmatched text., Return high-confidence hints without constructing an execution plan. (+11 more)

### Community 61 - "idempotency.py"
Cohesion: 0.18
Nodes (5): IdempotencyStore, InMemoryIdempotencyStore, MongoIdempotencyStore, Protocol, test_duplicate_request_is_claimed_only_once()

### Community 62 - "get_tw_stock_symbol_from_company_name"
Cohesion: 0.19
Nodes (7): interactive_test(), parse_args(), Interactive testing of the stock parser, Namespace, natural_language_routing_enabled(), Return whether unmatched natural-language requests use the new router., Financial request routing contracts and components.

### Community 63 - "LLMRouter"
Cohesion: 0.16
Nodes (17): Enum, AcceptanceReport, assert_acceptance_threshold(), evaluate_routes(), build_capability_requirements(), CapabilityConfig, Merge tool requirements and choose the strongest required model tier., validate_capability_registry() (+9 more)

### Community 64 - "handle_text_message"
Cohesion: 0.50
Nodes (3): fetch_stock_header_info(), Retrieve stock name, price, price change info, dividend yield, and TTM cash divi, TestFetchStockHeaderInfo

### Community 65 - "SKILL.md"
Cohesion: 0.18
Nodes (10): Check for context, Ending Discovery, Guardrails, Handling Different Entry Points, OpenSpec Awareness, The Stance, What You Don't Have To Do, What You Might Do (+2 more)

### Community 66 - "chart_theme.py"
Cohesion: 0.19
Nodes (10): model_for_tier(), Resolve a tier through deployment configuration without provider coupling., ExecutionGraph, ExecutionNode, ExecutionRequirements, BaseModel, build_execution_graph(), Build a dependency graph for the tools and final synthesis step. (+2 more)

### Community 67 - "get_institues_buy_sell_today_result"
Cohesion: 0.27
Nodes (10): process_message(), Process one message using either the legacy parser or financial routing., FinancialExecutor, ExecutionPlan, test_executor_answers_clarification_without_tools(), test_executor_renders_simple_market_data(), test_process_message_routes_recent_taiwan_market_request(), test_process_message_routes_taiwan_company_name_to_issuer() (+2 more)

### Community 68 - "groq_helper.py"
Cohesion: 0.43
Nodes (5): RouteCandidate, RouteDecision, LLMRouter, Protocol, SemanticRouter

### Community 69 - "ExecutionPlan"
Cohesion: 0.50
Nodes (5): create_response(), lambda_handler(), Any, AWS Lambda function to handle Line Messaging API webhooks., Create HTTP response for API Gateway      Args:         status_code: HTTP status

### Community 71 - "TestQuoteStock"
Cohesion: 0.22
Nodes (5): Test cases for quote_stock function, Test successful stock price fetch using yfinance, Test when stock symbol is not found, Test when yfinance fails, TestQuoteStock

### Community 72 - "Financial Request Routing Operational Guide & Release Checklist"
Cohesion: 0.25
Nodes (7): 1. Operational Configuration, 2. Intended LINE Contexts, 3. Data Source Limitations & Fallback Matrix, 4. Safety Mode Policy, 5. Rollback Procedure, 6. Release Checklist, Financial Request Routing Operational Guide & Release Checklist

### Community 73 - "observability.py"
Cohesion: 0.39
Nodes (6): Logger, anonymize_user_id(), log_routing(), routing_log_fields(), test_evaluation_set_covers_all_declared_capabilities(), test_observability_excludes_raw_user_message()

### Community 74 - "Financial routing inventory"
Cohesion: 0.50
Nodes (3): Existing data and LLM helpers, Financial routing inventory, LINE entry point

## Knowledge Gaps
- **169 isolated node(s):** `$schema`, `./claude/CLAUDE.md`, `deploy.sh script`, `init.sh script`, `local.sh script` (+164 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `parse_line_command()` connect `Command Parser & Mappings` to `LINE Webhook & Flex`, `get_institues_buy_sell_today_result`, `command_parser.py`, `output.py`, `opencode_helper.py`, `get_ups_or_downs`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Why does `handle_text_message()` connect `LINE Webhook & Flex` to `Command Parser & Mappings`, `get_institues_buy_sell_today_result`, `observability.py`, `opencode_helper.py`, `get_ups_or_downs`, `get_tw_stock_symbol_from_company_name`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Why does `get_tw_stock_price()` connect `command_parser.py` to `handle_text_message`, `Taiwan Stock Data`, `Fugle Quote Charts`, `OpenCode Inference`, `AWS & Broker Helpers`, `TestApp`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Are the 24 inferred relationships involving `parse_line_command()` (e.g. with `process_message()` and `handle_text_message()`) actually correct?**
  _`parse_line_command()` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `FinancialContext` (e.g. with `process_message()` and `handle_text_message()`) actually correct?**
  _`FinancialContext` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `ExecutionPlan` (e.g. with `process_message()` and `handle_text_message()`) actually correct?**
  _`ExecutionPlan` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `handle_text_message()` (e.g. with `parse_line_command()` and `enqueue_financial_request()`) actually correct?**
  _`handle_text_message()` has 16 INFERRED edges - model-reasoned connections that need verification._