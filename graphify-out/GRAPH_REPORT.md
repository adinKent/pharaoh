# Graph Report - pharaoh  (2026-10-05)

## Corpus Check
- 120 files · ~49,839 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 914 nodes · 1482 edges · 77 communities (59 shown, 18 thin omitted)
- Extraction: 78% EXTRACTED · 22% INFERRED · 0% AMBIGUOUS · INFERRED: 321 edges (avg confidence: 0.75)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a052b03c`
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
- SKILL.md
- chart_theme.py
- get_institues_buy_sell_today_result
- groq_helper.py
- TestQuoteStock
- Financial Request Routing Operational Guide & Release Checklist
- observability.py
- Financial routing inventory

## God Nodes (most connected - your core abstractions)
1. `parse_line_command()` - 33 edges
2. `FinancialContext` - 30 edges
3. `ExecutionPlan` - 27 edges
4. `TestParseLineCommand` - 24 edges
5. `EntityReference` - 21 edges
6. `ToolResult` - 20 edges
7. `FinancialRouter` - 19 edges
8. `Capability` - 18 edges
9. `handle_text_message()` - 17 edges
10. `get_tw_stock_price()` - 16 edges

## Surprising Connections (you probably didn't know these)
- `Development Requirements` --semantically_similar_to--> `Runtime Requirements`  [INFERRED] [semantically similar]
  requirements-dev.txt → src/requirements.txt
- `test_evaluation_set_covers_all_declared_capabilities()` --indirect_call--> `Capability`  [INFERRED]
  tests/unit/routing/test_observability_evaluation.py → src/routing/models.py
- `google-genai` --semantically_similar_to--> `google-genai`  [INFERRED] [semantically similar]
  requirements-dev.txt → src/requirements.txt
- `test_natural_language_routing_is_disabled_when_flag_is_false()` --calls--> `handle_text_message()`  [INFERRED]
  tests/unit/test_app_routing.py → src/app.py
- `process_message()` --calls--> `parse_line_command()`  [INFERRED]
  interactive_stock_test.py → src/line/command_parser.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Chart Design Pillars** — _claude_skills_image_response_design_skill_color_tokens, _claude_skills_image_response_design_skill_tw_polarity, _claude_skills_image_response_design_skill_palette_validation, _claude_skills_image_response_design_skill_intraday_layout [EXTRACTED 1.00]

## Communities (77 total, 18 thin omitted)

### Community 0 - "Command Parser & Mappings"
Cohesion: 0.08
Nodes (17): handle_ex_dividend_quote(), parse_line_command(), If text starts with '#', extract the symbol and return it with market type., Test cases for parse_line_command function, Test getting Taiwan stock info, Test getting US stock info, A partial Yahoo row must not make every moving average NaN., NaN moving averages (too little history) must not be written into the output. (+9 more)

### Community 1 - "Chart Rendering"
Cohesion: 0.12
Nodes (15): aggregate_dividend_records(), fetch_dividends_yfinance(), fetch_stock_header_info(), fetch_tw_stock_dividends_finmind(), generate_dividend_chart_png(), Aggregate records: past 5 years into annual sums, current year into individual p, Retrieve stock name, price, price change info, dividend yield, and TTM cash divi, Fetch dividend data, aggregate records, render stacked bar chart, and return ima (+7 more)

### Community 2 - "Taiwan Stock Data"
Cohesion: 0.12
Nodes (21): _extract_autocomplete_company_name(), format_total_net_diff(), format_twse_buy_and_sell_result(), get_institues_buy_sell_today_result(), get_today_ex_dividend_stocks(), get_tpex_ex_dividend_stocks(), get_tw_stock_name(), get_tw_stock_name_from_tpex() (+13 more)

### Community 3 - "LINE Webhook & Flex"
Cohesion: 0.06
Nodes (31): FlexMessage, MessagingApi, create_candidate_commands_flex(), create_response(), handle_text_message(), lambda_handler(), mark_message_as_read(), Any (+23 more)

### Community 4 - "Fugle Quote Charts"
Cohesion: 0.10
Nodes (20): DataFrame, _fallback_stock_price(), _fugle_history_df(), get_tw_index_price(), get_tw_stock_price(), get_tw_stock_year_candles_png(), _period_to_days(), Get real-time index price for a Taiwan index symbol using fugle.     Fugle takes (+12 more)

### Community 5 - "OpenCode Inference"
Cohesion: 0.08
Nodes (45): datetime, answer_data_status(), source_note(), natural_language_routing_enabled(), Return the deployment-scoped safety mode., Return whether unmatched natural-language requests use the new router., safety_mode(), choose_best_result() (+37 more)

### Community 6 - "AWS & Broker Helpers"
Cohesion: 0.24
Nodes (8): ChartTheme, get_chart_theme(), Color tokens for chart image responses.  Single source of truth for every color, Return the active theme. Selected via CHART_THEME env var; defaults to tradingvi, format_stock_price_response(), get_info_for_day_candle_picture(), Get icon representation for ups or downs status, Get icon representation for ups or downs status

### Community 7 - "Command Parser Tests"
Cohesion: 0.15
Nodes (7): Test cases for get_stock_symbol_and_marke_type function, Test parsing valid stock symbols starting with #, Test parsing with leading/trailing spaces, Test various invalid formats, Test fixed commands like #大盤, #美股, etc., Test tw company commands like #台積電, #長榮, etc., TestGetStockSymbolAndMarketType

### Community 8 - "OpenCode Helper Tests"
Cohesion: 0.22
Nodes (5): Test cases for format_stock_price_response function, Test formatting when price is up, Test formatting when price is down, Test formatting when price is unchanged, TestFormatStockPriceResponse

### Community 10 - "Architecture Docs"
Cohesion: 0.17
Nodes (10): AWS SAM Container Lambdas, LINE Messaging API Bot, Pharaoh, Trust Code Over README Boilerplate, S3 Presigned URL Image Reply, AWS Lambda, AWS SAM, CloudWatch (+2 more)

### Community 11 - "Serverless Infrastructure"
Cohesion: 0.07
Nodes (25): FinancialContext, MongoClient, RouteDecision, lambda_handler(), get_symbol_buy_sell_today_result(), enqueue_financial_request(), FinancialRequestJob, MongoRequestStatusStore (+17 more)

### Community 12 - "NVDA Yearly Chart"
Cohesion: 0.18
Nodes (11): NVDA 1-Year Candlestick Chart, Period High 236.26, Period Low 164.08, 20-Day MA 202.12, 5-Day MA 207.61, 60-Day MA 208.85, Current Price 202.81 (-2.21%), NVIDIA Corporation (NVDA) (+3 more)

### Community 13 - "Yahoo Finance Tests"
Cohesion: 0.17
Nodes (14): get_effective_date(), get_tpex_buy_sell_today_result(), get_twse_buy_sell_today_result(), normalize_tpex_stock_buy_sell_to_db_format(), normalize_twse_stock_buy_sell_to_db_format(), previous_working_day(), Downloads and parses the foreign and other investor trade summary from TWSE., Downloads and parses the foreign and other investor trade summary from TPEX. (+6 more)

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
Cohesion: 0.10
Nodes (29): OpenAI, build_line_command_prompt(), _chat_with_tools(), generate_openai_technical_analysis_response(), get_openai_client(), get_source_session_id(), infer_line_candidate_commands(), infer_line_command() (+21 more)

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
Cohesion: 0.27
Nodes (11): format_symbol_buy_sell_response(), get_stock_symbol_and_market_type(), get_tw_futopt_price(), handle_buy_and_sell_quote(), handle_day_k_line(), handle_stock_basic_analysis_quote(), handle_stock_dividend_chart(), handle_stock_price_quote() (+3 more)

### Community 38 - "get_tw_futopt_price"
Cohesion: 0.14
Nodes (15): ContextStore, ConversationContext, InMemoryContextStore, MongoContextStore, BaseModel, Protocol, Persist context using the project's existing MongoDB configuration., WorkflowState (+7 more)

### Community 39 - "TestFormatStockPriceResponse"
Cohesion: 0.22
Nodes (7): completion(), response(), response_tool_call(), test_generate_response_runs_tool_calls(), test_generate_response_uses_main_model(), test_infer_line_command_ignores_low_confidence(), test_infer_line_command_returns_high_confidence_candidate()

### Community 40 - "Financial AI Chatbot Context"
Cohesion: 0.40
Nodes (4): Data requirements, Financial AI Chatbot Context, Operating modes, Request routing

### Community 50 - "financial_ai_request_routing_proposal.md"
Cohesion: 0.05
Nodes (40): 10. Layer 4: Semantic Router, 11. Layer 5: LLM Router, 12. Freshness Routing, 13. Execution Plan, 14. Capability to Tool Mapping, 15. Model Routing, 16. Main Router Implementation, 17. Planner and Router Should Be Separate (+32 more)

### Community 53 - "fugle.py"
Cohesion: 0.10
Nodes (20): Figure, _build_candles_figure(), _get_api_key(), get_tw_stock_candles_png(), get_tw_stock_candles_png_bytes(), quote_stock_candles(), quote_stock_historical_candles(), quote_stock_ticker() (+12 more)

### Community 54 - "models.py"
Cohesion: 0.09
Nodes (22): get_all_commands(), get_fixed_command_examples(), Return fixed aliases and their backend symbols for inference context., build_clarification_plan(), Build a plan that asks the user for missing information before tool use., EntityResolution, The result of resolving user text to zero or more canonical entities., Resolve a single user-provided symbol or known fixed alias. (+14 more)

### Community 55 - "test_entities_and_rules.py"
Cohesion: 0.21
Nodes (7): get_stock_symbol_from_fixed_command(), Test #台指期 command maps to TXFR1 with TW_FUT market type, Test #台積期 command maps to CDFR1 with TW_FUT market type, Test unknown command should return None, Test cases for get_stock_symbol_from_fixed_command function, Test #美股 command returns list of US indices, TestGetStockSymbolFromFixedCommand

### Community 56 - "FinancialContext"
Cohesion: 0.22
Nodes (7): Command grammar (the bot's user interface), Commands, Config & secrets, graphify, Quote data sources, Tests, What this is

### Community 57 - "output.py"
Cohesion: 0.12
Nodes (12): format_analysis_output(), format_cash_dividend(), format_ex_dividend_response(), get_ups_or_downs(), Determine if the stock price is up, down, or unchanged.     Returns 1 for up, -1, Test cases for get_ups_or_downs function, Test when current price is higher than previous close, Test when current price is lower than previous close (+4 more)

### Community 59 - "TestApp"
Cohesion: 0.11
Nodes (25): draw_turnover_header(), get_x_label_align(), load_chart_font_name(), Shared chart-rendering helpers used by both the TW (Fugle) and US/foreign (yfina, Register the bundled Noto Sans TC font and return its family name., Render the top-right turnover block: label / number / unit columns, right-aligne, Save the figure locally (dev) or upload to S3 and return a presigned URL (Lambda, save_or_upload_fig() (+17 more)

### Community 60 - "get_ups_or_downs"
Cohesion: 0.16
Nodes (19): build_capability_requirements(), CapabilityConfig, Merge tool requirements and choose the strongest required model tier., FinancialContext, _extract_entities(), FinancialRouter, _has_valid_workflow_continuation(), Resolve token-like symbols and retain already resolved conversation entities. (+11 more)

### Community 62 - "get_tw_stock_symbol_from_company_name"
Cohesion: 0.26
Nodes (6): FinancialExecutor, ExecutionPlan, test_executor_answers_clarification_without_tools(), test_executor_renders_simple_market_data(), test_execution_plan_accepts_typed_entities_and_model_tier(), test_execution_plan_rejects_unknown_model_tier()

### Community 63 - "LLMRouter"
Cohesion: 0.22
Nodes (12): Enum, AcceptanceReport, assert_acceptance_threshold(), evaluate_routes(), RoutingCase, Financial request routing contracts and components., Capability, EntityKind (+4 more)

### Community 65 - "SKILL.md"
Cohesion: 0.18
Nodes (10): Check for context, Ending Discovery, Guardrails, Handling Different Entry Points, OpenSpec Awareness, The Stance, What You Don't Have To Do, What You Might Do (+2 more)

### Community 66 - "chart_theme.py"
Cohesion: 0.18
Nodes (11): model_for_tier(), Resolve a tier through deployment configuration without provider coupling., ExecutionGraph, ExecutionNode, ExecutionRequirements, Message, BaseModel, build_execution_graph() (+3 more)

### Community 67 - "get_institues_buy_sell_today_result"
Cohesion: 0.24
Nodes (10): interactive_test(), parse_args(), process_message(), Process one message using either the legacy parser or financial routing., Interactive testing of the stock parser, Namespace, test_process_message_routes_recent_taiwan_market_request(), test_process_message_routes_taiwan_company_name_to_issuer() (+2 more)

### Community 68 - "groq_helper.py"
Cohesion: 0.31
Nodes (7): validate_capability_registry(), RouteCandidate, RouteDecision, LLMRouter, Protocol, SemanticRouter, test_all_declared_capabilities_have_configuration()

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
- **169 isolated node(s):** `1. Contracts and compatibility foundation`, `2. Entity resolution and routing`, `3. Planner and capability registry`, `4. Freshness and answer generation`, `5. Workflow state and context` (+164 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `parse_line_command()` connect `Command Parser & Mappings` to `LINE Webhook & Flex`, `get_institues_buy_sell_today_result`, `command_parser.py`, `opencode_helper.py`, `get_ups_or_downs`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Why does `get_tw_stock_price()` connect `Fugle Quote Charts` to `Chart Rendering`, `Taiwan Stock Data`, `TestApp`, `OpenCode Inference`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Why does `EntityReference` connect `OpenCode Inference` to `chart_theme.py`, `groq_helper.py`, `get_tw_futopt_price`, `models.py`, `get_ups_or_downs`, `get_tw_stock_symbol_from_company_name`, `LLMRouter`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Are the 24 inferred relationships involving `parse_line_command()` (e.g. with `process_message()` and `handle_text_message()`) actually correct?**
  _`parse_line_command()` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `FinancialContext` (e.g. with `process_message()` and `lambda_handler()`) actually correct?**
  _`FinancialContext` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `ExecutionPlan` (e.g. with `process_message()` and `AcceptanceReport`) actually correct?**
  _`ExecutionPlan` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `EntityReference` (e.g. with `ContextStore` and `ConversationContext`) actually correct?**
  _`EntityReference` has 10 INFERRED edges - model-reasoned connections that need verification._