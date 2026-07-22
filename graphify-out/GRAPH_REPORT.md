# Graph Report - pharaoh  (2026-07-23)

## Corpus Check
- 35 files · ~18,245 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 352 nodes · 516 edges · 25 communities (20 shown, 5 thin omitted)
- Extraction: 79% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 107 edges (avg confidence: 0.81)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `86271d53`
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
- Command Parser Handlers
- TW Stock Price Fetch Tests
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
- CLAUDE.md

## God Nodes (most connected - your core abstractions)
1. `parse_line_command()` - 21 edges
2. `TestParseLineCommand` - 16 edges
3. `get_stock_symbol_and_market_type()` - 13 edges
4. `get_tw_stock_candles_png()` - 12 edges
5. `get_tw_stock_price()` - 11 edges
6. `get_us_stock_candles_png()` - 11 edges
7. `NVDA 1-Year Candlestick Chart` - 10 edges
8. `get_stock_symbol_from_fixed_command()` - 9 edges
9. `TestGetStockSymbolFromFixedCommand` - 9 edges
10. `handle_text_message()` - 9 edges

## Surprising Connections (you probably didn't know these)
- `README Template Boilerplate` --semantically_similar_to--> `Pharaoh Project Overview`  [INFERRED] [semantically similar]
  README.md → .claude/CLAUDE.md
- `interactive_test()` --calls--> `parse_line_command()`  [INFERRED]
  interactive_stock_test.py → src/line/command_parser.py
- `get_tw_stock_candles_png()` --calls--> `quote_stock_ticker()`  [INFERRED]
  src/quote/tw_stock.py → src/quote/fugle.py
- `get_tw_stock_candles_png()` --calls--> `quote_stock_candles()`  [INFERRED]
  src/quote/tw_stock.py → src/quote/fugle.py
- `LineWebhookFunction (SAM)` --implements--> `line-webhook Lambda`  [INFERRED]
  infrastructure/template.yaml → .claude/CLAUDE.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Market-Type Quote Source Routing** — _claude_claude_md_symbol_resolution, _claude_claude_md_fugle_source, _claude_claude_md_shioaji_source, _claude_claude_md_yfinance_source [EXTRACTED 1.00]
- **Chart Design Pillars** — _claude_skills_image_response_design_skill_color_tokens, _claude_skills_image_response_design_skill_tw_polarity, _claude_skills_image_response_design_skill_palette_validation, _claude_skills_image_response_design_skill_intraday_layout [EXTRACTED 1.00]
- **SAM Lambda Stack Composition** — infrastructure_template_yaml_linewebhookfunction, infrastructure_template_yaml_linewebhookapi, infrastructure_template_yaml_linewebhookfunctionrole, infrastructure_template_yaml_imagebucket, infrastructure_template_yaml_deadletterqueue [EXTRACTED 1.00]

## Communities (25 total, 5 thin omitted)

### Community 0 - "TW Stock Data Sync"
Cohesion: 0.07
Nodes (40): MongoClient, _extract_autocomplete_company_name(), format_total_net_diff(), _format_trade_value(), format_twse_buy_and_sell_result(), get_effective_date(), get_institues_buy_sell_today_result(), get_symbol_buy_sell_today_result() (+32 more)

### Community 1 - "LINE Webhook Handler"
Cohesion: 0.08
Nodes (24): Any, MessagingApi, create_response(), handle_text_message(), lambda_handler(), mark_message_as_read(), Uses the Line SDK's underlying ApiClient to mark a message as read., Create HTTP response for API Gateway      Args:         status_code: HTTP status (+16 more)

### Community 2 - "Fugle Quote & Chart"
Cohesion: 0.13
Nodes (16): Figure, _build_candles_figure(), _get_api_key(), get_tw_stock_candles_png(), get_tw_stock_candles_png_bytes(), quote_stock_candles(), quote_stock_ticker(), upload_tw_stock_candles_png_to_s3() (+8 more)

### Community 3 - "Chart Rendering Shared"
Cohesion: 0.12
Nodes (29): draw_turnover_header(), get_x_label_align(), load_chart_font_name(), Shared chart-rendering helpers used by both the TW (Fugle) and US/foreign (yfina, Register the bundled Noto Sans TC font and return its family name., Render the top-right turnover block: label / number / unit columns, right-aligne, Save the figure locally (dev) or upload to S3 and return a presigned URL (Lambda, save_or_upload_fig() (+21 more)

### Community 4 - "Quote Output Formatting"
Cohesion: 0.12
Nodes (15): format_analysis_output(), format_cash_dividend(), format_ex_dividend_response(), format_price_output(), format_stock_price_response(), get_ups_or_downs(), Determine if the stock price is up, down, or unchanged.     Returns 1 for up, -1, Get icon representation for ups or downs status (+7 more)

### Community 5 - "Command Parser Tests"
Cohesion: 0.47
Nodes (3): completion(), test_generate_response_retries_with_fallback_model(), test_generate_response_uses_main_model()

### Community 6 - "AWS SAM Infrastructure"
Cohesion: 0.13
Nodes (17): line-webhook Lambda, Pharaoh Project Overview, SSM Parameter Store Secrets, sync-tw-data Lambda, TWSE/TPEX Open APIs, DeadLetterQueue (SQS), ImageBucket (S3), LineWebhookApi Gateway (+9 more)

### Community 7 - "Fixed Command Mappings"
Cohesion: 0.11
Nodes (12): get_stock_symbol_from_fixed_command(), Test #台指期 command maps to TXFR1 with TW_FUT market type, Test #台積期 command maps to CDFR1 with TW_FUT market type, Test unknown command should return None, Test cases for format_stock_price_response function, Test formatting when price is up, Test formatting when price is down, Test formatting when price is unchanged (+4 more)

### Community 8 - "Project Concepts & Rationale"
Cohesion: 0.14
Nodes (16): Bot Command Grammar, Fugle Data Source, Gemini AI Commentary, Shared Quote Output Normalization, S3 Presigned URL Reply Contract, Shioaji/SinoPac Data Source, Symbol Resolution & Market Routing, yfinance Data Source (+8 more)

### Community 9 - "Interactive REPL & Dispatch"
Cohesion: 0.08
Nodes (19): interactive_test(), Interactive testing of the stock parser, handle_ex_dividend_quote(), parse_line_command(), If text starts with '#', extract the symbol and return it with market type., Test cases for parse_line_command function, Test getting Taiwan stock info, Test getting US stock info (+11 more)

### Community 10 - "Command Parser Handlers"
Cohesion: 0.19
Nodes (7): format_symbol_buy_sell_response(), get_tw_futopt_price(), handle_buy_and_sell_quote(), handle_stock_price_quote(), Formats the buy/sell data into a readable string., Test get_tw_futopt_price returns formatted dict., Test get_tw_futopt_price returns formatted dict for TSMC futures.

### Community 11 - "TW Stock Price Fetch Tests"
Cohesion: 0.14
Nodes (13): _fallback_stock_price(), get_tw_index_price(), get_tw_stock_price(), Fallback method using Taiwan Stock Exchange API or web scraping., Get real-time stock price for a Taiwan stock symbol using fugle and yfinance lib, Get real-time index price for a Taiwan index symbol using fugle and yfinance lib, Test fallback using TWSE API, Test cases for get_tw_stock_price function (+5 more)

### Community 12 - "Symbol Resolution Tests"
Cohesion: 0.17
Nodes (10): get_stock_symbol_and_market_type(), handle_day_k_line(), handle_year_k_line(), Test cases for get_stock_symbol_and_marke_type function, Test parsing valid stock symbols starting with #, Test parsing with leading/trailing spaces, Test various invalid formats, Test fixed commands like #大盤, #美股, etc. (+2 more)

### Community 13 - "NVDA Yearly Chart Image"
Cohesion: 0.18
Nodes (11): NVDA 1-Year Candlestick Chart, Period High 236.26, Period Low 164.08, 20-Day MA 202.12, 5-Day MA 207.61, 60-Day MA 208.85, Current Price 202.81 (-2.21%), NVIDIA Corporation (NVDA) (+3 more)

### Community 14 - "Price Response Format Tests"
Cohesion: 0.67
Nodes (3): handle_stock_basic_analysis_quote(), generate_groq_technical_analysis_response(), get_groq_client()

### Community 15 - "Yahoo Finance Tests"
Cohesion: 0.22
Nodes (5): Test cases for quote_stock function, Test successful stock price fetch using yfinance, Test when stock symbol is not found, Test when yfinance fails, TestQuoteStock

### Community 16 - "NVDA Intraday Chart Image"
Cohesion: 0.25
Nodes (8): NVDA Intraday Chart, Intraday High 206.65, Intraday Low 197.97, Price 202.81 (-4.59, -2.21%), US Session 09:30-16:00, yfinance data source, NVIDIA Corporation (NVDA), Turnover 126.8M

### Community 17 - "OHI Intraday Chart Image"
Cohesion: 0.29
Nodes (7): OHI Intraday Chart, Day High 50.75 / Low 49.71, Intraday Price 50.21 (+0.68%), Data source: yfinance (US intraday), Omega Healthcare Investors (OHI), Trend: morning peak, midday dip, late-day recovery, Trade Turnover 1.5M

## Knowledge Gaps
- **38 isolated node(s):** `init.sh script`, `deploy.sh script`, `local.sh script`, `graphify`, `Shioaji/SinoPac Data Source` (+33 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `parse_line_command()` connect `Interactive REPL & Dispatch` to `LINE Webhook Handler`, `Command Parser Handlers`, `Symbol Resolution Tests`, `Price Response Format Tests`?**
  _High betweenness centrality (0.095) - this node is a cross-community bridge._
- **Why does `get_stock_symbol_and_market_type()` connect `Symbol Resolution Tests` to `Command Parser Handlers`, `Price Response Format Tests`, `Fixed Command Mappings`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Why does `get_tw_stock_price()` connect `TW Stock Price Fetch Tests` to `TW Stock Data Sync`, `Chart Rendering Shared`, `Quote Output Formatting`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `parse_line_command()` (e.g. with `interactive_test()` and `handle_text_message()`) actually correct?**
  _`parse_line_command()` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `get_stock_symbol_and_market_type()` (e.g. with `.test_edge_cases()` and `.test_fixed_commands()`) actually correct?**
  _`get_stock_symbol_and_market_type()` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `get_tw_stock_candles_png()` (e.g. with `draw_turnover_header()` and `get_x_label_align()`) actually correct?**
  _`get_tw_stock_candles_png()` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `get_tw_stock_price()` (e.g. with `format_price_output()` and `.test_fallback_when_fugle_fails()`) actually correct?**
  _`get_tw_stock_price()` has 5 INFERRED edges - model-reasoned connections that need verification._