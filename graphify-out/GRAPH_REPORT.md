# Graph Report - .  (2026-08-30)

## Corpus Check
- Corpus is ~21,383 words - fits in a single context window. You may not need a graph.

## Summary
- 420 nodes · 632 edges · 27 communities (23 shown, 4 thin omitted)
- Extraction: 82% EXTRACTED · 18% INFERRED · 0% AMBIGUOUS · INFERRED: 116 edges (avg confidence: 0.81)
- Token cost: 0 input · 0 output

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

## God Nodes (most connected - your core abstractions)
1. `parse_line_command()` - 27 edges
2. `TestParseLineCommand` - 20 edges
3. `get_tw_stock_price()` - 15 edges
4. `get_stock_symbol_and_market_type()` - 14 edges
5. `handle_text_message()` - 12 edges
6. `TestApp` - 12 edges
7. `get_us_stock_candles_png()` - 11 edges
8. `NVDA 1-Year Candlestick Chart` - 10 edges
9. `get_us_stock_year_candles_png()` - 9 edges
10. `get_stock_symbol_from_fixed_command()` - 9 edges

## Surprising Connections (you probably didn't know these)
- `Development Requirements` --semantically_similar_to--> `Runtime Requirements`  [INFERRED] [semantically similar]
  requirements-dev.txt → src/requirements.txt
- `google-genai` --semantically_similar_to--> `google-genai`  [INFERRED] [semantically similar]
  requirements-dev.txt → src/requirements.txt
- `Ruff Pre-Commit Hooks` --conceptually_related_to--> `Conda Environment Spec (pharaoh)`  [INFERRED]
  .pre-commit-config.yaml → environment.yml
- `interactive_test()` --calls--> `parse_line_command()`  [INFERRED]
  interactive_stock_test.py → src/line/command_parser.py
- `handle_buy_and_sell_quote()` --calls--> `get_symbol_buy_sell_today_result()`  [INFERRED]
  src/line/command_parser.py → src/quote/tw_stock.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Pharaoh Serverless LINE Architecture** — claude_claude_line_messaging_api_bot, infrastructure_template_line_webhook_function, infrastructure_template_line_webhook_api, infrastructure_template_image_bucket [EXTRACTED 1.00]
- **Dual Lambda Container Deployment** — claude_claude_aws_sam_container_lambdas, infrastructure_template_line_webhook_function, infrastructure_template_sync_tw_data_function, infrastructure_ecr_line_webhook_repository, infrastructure_ecr_sync_tw_data_repository [EXTRACTED 1.00]
- **Chart Design Pillars** — _claude_skills_image_response_design_skill_color_tokens, _claude_skills_image_response_design_skill_tw_polarity, _claude_skills_image_response_design_skill_palette_validation, _claude_skills_image_response_design_skill_intraday_layout [EXTRACTED 1.00]

## Communities (27 total, 4 thin omitted)

### Community 0 - "Command Parser & Mappings"
Cohesion: 0.06
Nodes (34): interactive_test(), Interactive testing of the stock parser, format_symbol_buy_sell_response(), get_stock_symbol_and_market_type(), get_tw_futopt_price(), handle_buy_and_sell_quote(), handle_day_k_line(), handle_ex_dividend_quote() (+26 more)

### Community 1 - "Chart Rendering"
Cohesion: 0.06
Nodes (39): draw_turnover_header(), get_x_label_align(), load_chart_font_name(), Shared chart-rendering helpers used by both the TW (Fugle) and US/foreign (yfina, Register the bundled Noto Sans TC font and return its family name., Render the top-right turnover block: label / number / unit columns, right-aligne, Save the figure locally (dev) or upload to S3 and return a presigned URL (Lambda, save_or_upload_fig() (+31 more)

### Community 2 - "Taiwan Stock Data"
Cohesion: 0.08
Nodes (35): _extract_autocomplete_company_name(), format_total_net_diff(), format_twse_buy_and_sell_result(), get_effective_date(), get_institues_buy_sell_today_result(), get_symbol_buy_sell_today_result(), get_today_ex_dividend_stocks(), get_tpex_buy_sell_today_result() (+27 more)

### Community 3 - "LINE Webhook & Flex"
Cohesion: 0.08
Nodes (27): Any, FlexMessage, MessagingApi, create_candidate_commands_flex(), create_response(), handle_text_message(), lambda_handler(), mark_message_as_read() (+19 more)

### Community 4 - "Fugle Quote Charts"
Cohesion: 0.07
Nodes (29): DataFrame, Figure, _build_candles_figure(), get_tw_stock_candles_png(), get_tw_stock_candles_png_bytes(), quote_stock_candles(), quote_stock_historical_candles(), quote_stock_ticker() (+21 more)

### Community 5 - "OpenCode Inference"
Cohesion: 0.15
Nodes (23): _chat_with_tools(), generate_opencode_technical_analysis_response(), get_opencode_client(), infer_line_candidate_commands(), infer_line_command(), _is_valid_line_command(), _message_to_dict(), Infer up to three supported LINE commands, ordered by confidence. (+15 more)

### Community 6 - "AWS & Broker Helpers"
Cohesion: 0.14
Nodes (14): MongoClient, _get_api_key(), _get_api_secret(), get_futopt_snapshot(), Get a one-shot futures/options snapshot from SinoPac's shioaji API.     Returns, get_secret(), get_ssm_parameter(), Fetches a parameter from AWS SSM Parameter Store, using a cache. (+6 more)

### Community 7 - "Command Parser Tests"
Cohesion: 0.11
Nodes (10): Test cases for format_stock_price_response function, Test formatting when price is up, Test cases for get_stock_symbol_and_marke_type function, Test parsing valid stock symbols starting with #, Test parsing with leading/trailing spaces, Test various invalid formats, Test fixed commands like #大盤, #美股, etc., Test tw company commands like #台積電, #長榮, etc. (+2 more)

### Community 8 - "OpenCode Helper Tests"
Cohesion: 0.24
Nodes (10): completion(), test_generate_response_handles_tool_calls(), test_generate_response_prefetches_market_search(), test_generate_response_retries_with_fallback_model(), test_generate_response_uses_main_model(), test_infer_line_candidate_commands_returns_ranked_candidates(), test_infer_line_command_rejects_low_confidence_candidate(), test_infer_line_command_retries_with_fallback_model() (+2 more)

### Community 9 - "Fixed Command Tests"
Cohesion: 0.24
Nodes (6): get_stock_symbol_from_fixed_command(), Test #台指期 command maps to TXFR1 with TW_FUT market type, Test unknown command should return None, Test cases for get_stock_symbol_from_fixed_command function, Test #美股 command returns list of US indices, TestGetStockSymbolFromFixedCommand

### Community 10 - "Architecture Docs"
Cohesion: 0.17
Nodes (10): AWS SAM Container Lambdas, LINE Messaging API Bot, Pharaoh, Trust Code Over README Boilerplate, S3 Presigned URL Image Reply, AWS Lambda, AWS SAM, CloudWatch (+2 more)

### Community 11 - "Serverless Infrastructure"
Cohesion: 0.25
Nodes (11): ECR Bootstrap Template, LineWebhookRepository, SyncTwDataRepository, DeadLetterQueue, ImageBucket, LineWebhookApi, LineWebhookFunction, LineWebhookFunctionRole (+3 more)

### Community 12 - "NVDA Yearly Chart"
Cohesion: 0.18
Nodes (11): NVDA 1-Year Candlestick Chart, Period High 236.26, Period Low 164.08, 20-Day MA 202.12, 5-Day MA 207.61, 60-Day MA 208.85, Current Price 202.81 (-2.21%), NVIDIA Corporation (NVDA) (+3 more)

### Community 13 - "Yahoo Finance Tests"
Cohesion: 0.22
Nodes (5): Test cases for quote_stock function, Test successful stock price fetch using yfinance, Test when stock symbol is not found, Test when yfinance fails, TestQuoteStock

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

## Knowledge Gaps
- **41 isolated node(s):** `local.sh script`, `dataviz skill (referenced)`, `Ruff Pre-Commit Hooks`, `Conda Environment Spec (pharaoh)`, `NVIDIA Corporation (NVDA)` (+36 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `parse_line_command()` connect `Command Parser & Mappings` to `LINE Webhook & Flex`, `OpenCode Inference`?**
  _High betweenness centrality (0.107) - this node is a cross-community bridge._
- **Why does `get_tw_stock_price()` connect `Fugle Quote Charts` to `Command Parser & Mappings`, `Taiwan Stock Data`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Why does `get_stock_symbol_and_market_type()` connect `Command Parser & Mappings` to `Fixed Command Tests`, `Taiwan Stock Data`, `Command Parser Tests`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Are the 19 inferred relationships involving `parse_line_command()` (e.g. with `interactive_test()` and `handle_text_message()`) actually correct?**
  _`parse_line_command()` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `get_tw_stock_price()` (e.g. with `handle_stock_basic_analysis_quote()` and `handle_stock_price_quote()`) actually correct?**
  _`get_tw_stock_price()` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `get_stock_symbol_and_market_type()` (e.g. with `get_tw_stock_symbol_from_company_name()` and `.test_edge_cases()`) actually correct?**
  _`get_stock_symbol_and_market_type()` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `handle_text_message()` (e.g. with `parse_line_command()` and `.test_text_message_event_no_command()`) actually correct?**
  _`handle_text_message()` has 5 INFERRED edges - model-reasoned connections that need verification._