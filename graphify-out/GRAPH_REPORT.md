# Graph Report - pharaoh  (2026-08-29)

## Corpus Check
- 39 files · ~20,645 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 395 nodes · 562 edges · 34 communities (29 shown, 5 thin omitted)
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 87 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4145e462`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- TW Stock Data Sync
- LINE Webhook Handler
- Fugle Quote & Chart
- Chart Rendering Shared
- Quote Output Formatting
- Command Parser Tests
- AWS SAM Infrastructure
- Fixed Command Mappings
- Project Concepts & Rationale
- Interactive REPL & Dispatch
- get_tw_stock_price
- command_parser.py
- Symbol Resolution Tests
- NVDA Yearly Chart Image
- Price Response Format Tests
- Yahoo Finance Tests
- NVDA Intraday Chart Image
- OHI Intraday Chart Image
- Deps & Tooling Config
- Deploy Script
- Init Script
- Local Dev Script
- format_stock_price_response
- CLAUDE.md
- get_tw_futopt_price
- test_tw_stock.py
- .test_basic_analysis_omits_nan_moving_averages
- format_twse_buy_and_sell_result
- get_tw_stock_candles_png
- _fallback_stock_price

## God Nodes (most connected - your core abstractions)
1. `parse_line_command()` - 22 edges
2. `TestParseLineCommand` - 17 edges
3. `get_stock_symbol_and_market_type()` - 13 edges
4. `get_tw_stock_price()` - 13 edges
5. `get_us_stock_candles_png()` - 11 edges
6. `TestApp` - 10 edges
7. `NVDA 1-Year Candlestick Chart` - 10 edges
8. `handle_text_message()` - 9 edges
9. `get_stock_symbol_from_fixed_command()` - 9 edges
10. `TestGetStockSymbolFromFixedCommand` - 9 edges

## Surprising Connections (you probably didn't know these)
- `README Template Boilerplate` --semantically_similar_to--> `Pharaoh Project Overview`  [INFERRED] [semantically similar]
  README.md → .claude/CLAUDE.md
- `interactive_test()` --calls--> `parse_line_command()`  [INFERRED]
  interactive_stock_test.py → src/line/command_parser.py
- `Ruff Pre-Commit Hooks` --conceptually_related_to--> `Conda Environment Spec (pharaoh)`  [INFERRED]
  .pre-commit-config.yaml → environment.yml
- `handle_text_message()` --calls--> `parse_line_command()`  [INFERRED]
  src/app.py → src/line/command_parser.py
- `save_or_upload_fig()` --calls--> `put_image()`  [INFERRED]
  src/quote/chart_common.py → src/utils/aws_helper.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Market-Type Quote Source Routing** — _claude_claude_md_symbol_resolution, _claude_claude_md_fugle_source, _claude_claude_md_shioaji_source, _claude_claude_md_yfinance_source [EXTRACTED 1.00]
- **Chart Design Pillars** — _claude_skills_image_response_design_skill_color_tokens, _claude_skills_image_response_design_skill_tw_polarity, _claude_skills_image_response_design_skill_palette_validation, _claude_skills_image_response_design_skill_intraday_layout [EXTRACTED 1.00]

## Communities (34 total, 5 thin omitted)

### Community 0 - "TW Stock Data Sync"
Cohesion: 0.20
Nodes (14): _extract_autocomplete_company_name(), get_today_ex_dividend_stocks(), get_tpex_ex_dividend_stocks(), get_tw_stock_name(), get_tw_stock_name_from_tpex(), get_tw_stock_name_from_twse(), get_tw_stock_symbol_from_company_name(), get_twse_ex_dividend_stocks() (+6 more)

### Community 1 - "LINE Webhook Handler"
Cohesion: 0.08
Nodes (24): Any, MessagingApi, create_response(), handle_text_message(), lambda_handler(), mark_message_as_read(), Uses the Line SDK to send a reply image., Uses the Line SDK's underlying ApiClient to mark a message as read. (+16 more)

### Community 2 - "Fugle Quote & Chart"
Cohesion: 0.15
Nodes (13): MongoClient, _get_api_key(), _get_api_key(), _get_api_secret(), get_futopt_snapshot(), Get a one-shot futures/options snapshot from SinoPac's shioaji API.     Returns, get_ssm_parameter(), Fetches a parameter from AWS SSM Parameter Store, using a cache. (+5 more)

### Community 3 - "Chart Rendering Shared"
Cohesion: 0.10
Nodes (27): draw_turnover_header(), get_x_label_align(), load_chart_font_name(), Shared chart-rendering helpers used by both the TW (Fugle) and US/foreign (yfina, Register the bundled Noto Sans TC font and return its family name., Render the top-right turnover block: label / number / unit columns, right-aligne, Save the figure locally (dev) or upload to S3 and return a presigned URL (Lambda, save_or_upload_fig() (+19 more)

### Community 4 - "Quote Output Formatting"
Cohesion: 0.12
Nodes (15): format_analysis_output(), format_cash_dividend(), format_ex_dividend_response(), format_price_output(), format_stock_price_response(), get_ups_or_downs(), Determine if the stock price is up, down, or unchanged.     Returns 1 for up, -1, Get icon representation for ups or downs status (+7 more)

### Community 5 - "Command Parser Tests"
Cohesion: 0.47
Nodes (3): completion(), test_generate_response_retries_with_fallback_model(), test_generate_response_uses_main_model()

### Community 6 - "AWS SAM Infrastructure"
Cohesion: 0.17
Nodes (14): get_effective_date(), get_tpex_buy_sell_today_result(), get_twse_buy_sell_today_result(), normalize_tpex_stock_buy_sell_to_db_format(), normalize_twse_stock_buy_sell_to_db_format(), previous_working_day(), Downloads and parses the foreign and other investor trade summary from TWSE., Downloads and parses the foreign and other investor trade summary from TPEX. (+6 more)

### Community 7 - "Fixed Command Mappings"
Cohesion: 0.11
Nodes (12): get_stock_symbol_from_fixed_command(), Test #台指期 command maps to TXFR1 with TW_FUT market type, Test #台積期 command maps to CDFR1 with TW_FUT market type, Test unknown command should return None, Test cases for format_stock_price_response function, Test formatting when price is up, Test formatting when price is down, Test formatting when price is unchanged (+4 more)

### Community 8 - "Project Concepts & Rationale"
Cohesion: 0.09
Nodes (24): Bot Command Grammar, Fugle Data Source, Gemini AI Commentary, line-webhook Lambda, Shared Quote Output Normalization, Pharaoh Project Overview, S3 Presigned URL Reply Contract, Shioaji/SinoPac Data Source (+16 more)

### Community 9 - "Interactive REPL & Dispatch"
Cohesion: 0.08
Nodes (19): interactive_test(), Interactive testing of the stock parser, handle_ex_dividend_quote(), parse_line_command(), If text starts with '#', extract the symbol and return it with market type., Test cases for parse_line_command function, Test getting Taiwan stock info, Test getting US stock info (+11 more)

### Community 10 - "get_tw_stock_price"
Cohesion: 0.12
Nodes (16): _fugle_history_df(), get_tw_index_price(), get_tw_stock_price(), get_tw_stock_year_candles_png(), _period_to_days(), Get real-time index price for a Taiwan index symbol using fugle.     Fugle takes, Map a yfinance-style period string to a calendar-day lookback for Fugle., Fetch ~`days` calendar days of daily candles from Fugle as a yfinance-shaped (+8 more)

### Community 11 - "command_parser.py"
Cohesion: 0.42
Nodes (8): format_symbol_buy_sell_response(), get_stock_symbol_and_market_type(), handle_buy_and_sell_quote(), handle_day_k_line(), handle_stock_basic_analysis_quote(), handle_stock_price_quote(), handle_year_k_line(), Formats the buy/sell data into a readable string.

### Community 12 - "Symbol Resolution Tests"
Cohesion: 0.15
Nodes (7): Test cases for get_stock_symbol_and_marke_type function, Test parsing valid stock symbols starting with #, Test parsing with leading/trailing spaces, Test various invalid formats, Test fixed commands like #大盤, #美股, etc., Test tw company commands like #台積電, #長榮, etc., TestGetStockSymbolAndMarketType

### Community 13 - "NVDA Yearly Chart Image"
Cohesion: 0.18
Nodes (11): NVDA 1-Year Candlestick Chart, Period High 236.26, Period Low 164.08, 20-Day MA 202.12, 5-Day MA 207.61, 60-Day MA 208.85, Current Price 202.81 (-2.21%), NVIDIA Corporation (NVDA) (+3 more)

### Community 14 - "Price Response Format Tests"
Cohesion: 0.21
Nodes (7): Figure, _build_candles_figure(), get_tw_stock_candles_png(), get_tw_stock_candles_png_bytes(), quote_stock_historical_candles(), Daily OHLCV candles between from_date and to_date (both YYYY-MM-DD, inclusive)., upload_tw_stock_candles_png_to_s3()

### Community 15 - "Yahoo Finance Tests"
Cohesion: 0.22
Nodes (5): Test cases for quote_stock function, Test successful stock price fetch using yfinance, Test when stock symbol is not found, Test when yfinance fails, TestQuoteStock

### Community 16 - "NVDA Intraday Chart Image"
Cohesion: 0.25
Nodes (8): NVDA Intraday Chart, Intraday High 206.65, Intraday Low 197.97, Price 202.81 (-4.59, -2.21%), US Session 09:30-16:00, yfinance data source, NVIDIA Corporation (NVDA), Turnover 126.8M

### Community 17 - "OHI Intraday Chart Image"
Cohesion: 0.29
Nodes (7): OHI Intraday Chart, Day High 50.75 / Low 49.71, Intraday Price 50.21 (+0.68%), Data source: yfinance (US intraday), Omega Healthcare Investors (OHI), Trend: morning peak, midday dip, late-day recovery, Trade Turnover 1.5M

### Community 24 - "format_stock_price_response"
Cohesion: 0.31
Nodes (6): completion(), test_generate_response_handles_tool_calls(), test_generate_response_prefetches_market_search(), test_generate_response_retries_with_fallback_model(), test_generate_response_uses_main_model(), tool_call()

### Community 25 - "CLAUDE.md"
Cohesion: 0.50
Nodes (3): instructions, $schema, ./claude/CLAUDE.md

### Community 26 - "get_tw_futopt_price"
Cohesion: 0.29
Nodes (4): get_tw_futopt_price(), Test get_tw_futopt_price returns formatted dict., Test get_tw_futopt_price returns None when snapshot fails., Test get_tw_futopt_price returns formatted dict for TSMC futures.

### Community 29 - ".test_basic_analysis_omits_nan_moving_averages"
Cohesion: 0.17
Nodes (18): _chat_with_tools(), generate_opencode_technical_analysis_response(), get_opencode_client(), _message_to_dict(), _run_tool(), _duckduckgo_instant_answer(), _fetch_text(), _format_us_info_value() (+10 more)

### Community 31 - "format_twse_buy_and_sell_result"
Cohesion: 0.40
Nodes (5): format_total_net_diff(), format_twse_buy_and_sell_result(), get_institues_buy_sell_today_result(), Format TWSE fund result JSON to a pretty text., Fetch today's buy sell result from TWSE using the provided URL format.     Forma

### Community 32 - "get_tw_stock_candles_png"
Cohesion: 0.50
Nodes (4): DataFrame, _format_trade_value(), get_tw_stock_candles_png(), Format a TWD trade value with a Chinese unit: 億 (1e8) once it reaches 億, else 萬

### Community 33 - "_fallback_stock_price"
Cohesion: 0.50
Nodes (3): _fallback_stock_price(), Fallback method using Taiwan Stock Exchange API or web scraping., Test fallback using TWSE API

## Knowledge Gaps
- **36 isolated node(s):** `init.sh script`, `$schema`, `./claude/CLAUDE.md`, `deploy.sh script`, `local.sh script` (+31 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `parse_line_command()` connect `Interactive REPL & Dispatch` to `LINE Webhook Handler`, `command_parser.py`?**
  _High betweenness centrality (0.095) - this node is a cross-community bridge._
- **Why does `get_tw_stock_price()` connect `get_tw_stock_price` to `TW Stock Data Sync`, `_fallback_stock_price`, `get_tw_stock_candles_png`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Why does `get_stock_symbol_and_market_type()` connect `command_parser.py` to `Symbol Resolution Tests`, `Fixed Command Mappings`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `parse_line_command()` (e.g. with `interactive_test()` and `handle_text_message()`) actually correct?**
  _`parse_line_command()` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `get_stock_symbol_and_market_type()` (e.g. with `.test_edge_cases()` and `.test_fixed_commands()`) actually correct?**
  _`get_stock_symbol_and_market_type()` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `get_tw_stock_price()` (e.g. with `.test_fallback_when_fugle_fails()` and `.test_fallback_when_history_fetch_fails()`) actually correct?**
  _`get_tw_stock_price()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `get_us_stock_candles_png()` (e.g. with `draw_turnover_header()` and `get_x_label_align()`) actually correct?**
  _`get_us_stock_candles_png()` has 7 INFERRED edges - model-reasoned connections that need verification._