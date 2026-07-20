# Graph Report - pharaoh  (2026-07-21)

## Corpus Check
- 33 files · ~17,543 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 343 nodes · 523 edges · 26 communities (22 shown, 4 thin omitted)
- Extraction: 76% EXTRACTED · 24% INFERRED · 0% AMBIGUOUS · INFERRED: 127 edges (avg confidence: 0.81)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `30c0d9a3`
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
- fugle.py
- CLAUDE.md

## God Nodes (most connected - your core abstractions)
1. `parse_line_command()` - 20 edges
2. `TestParseLineCommand` - 15 edges
3. `get_stock_symbol_and_market_type()` - 14 edges
4. `get_tw_stock_price()` - 13 edges
5. `get_tw_stock_candles_png()` - 12 edges
6. `get_us_stock_candles_png()` - 12 edges
7. `get_stock_symbol_from_fixed_command()` - 10 edges
8. `get_us_stock_year_candles_png()` - 10 edges
9. `NVDA 1-Year Candlestick Chart` - 10 edges
10. `handle_text_message()` - 9 edges

## Surprising Connections (you probably didn't know these)
- `README Template Boilerplate` --semantically_similar_to--> `Pharaoh Project Overview`  [INFERRED] [semantically similar]
  README.md → .claude/CLAUDE.md
- `Conda Environment Spec (pharaoh)` --semantically_similar_to--> `Lambda Python Requirements`  [INFERRED] [semantically similar]
  environment.yml → src/requirements.txt
- `Dev Python Requirements` --semantically_similar_to--> `Lambda Python Requirements`  [INFERRED] [semantically similar]
  requirements-dev.txt → src/requirements.txt
- `interactive_test()` --calls--> `parse_line_command()`  [INFERRED]
  interactive_stock_test.py → src/line/command_parser.py
- `get_tw_stock_candles_png()` --calls--> `quote_stock_ticker()`  [INFERRED]
  src/quote/tw_stock.py → src/quote/fugle.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Market-Type Quote Source Routing** — _claude_claude_md_symbol_resolution, _claude_claude_md_fugle_source, _claude_claude_md_shioaji_source, _claude_claude_md_yfinance_source [EXTRACTED 1.00]
- **Chart Design Pillars** — _claude_skills_image_response_design_skill_color_tokens, _claude_skills_image_response_design_skill_tw_polarity, _claude_skills_image_response_design_skill_palette_validation, _claude_skills_image_response_design_skill_intraday_layout [EXTRACTED 1.00]
- **SAM Lambda Stack Composition** — infrastructure_template_yaml_linewebhookfunction, infrastructure_template_yaml_linewebhookapi, infrastructure_template_yaml_linewebhookfunctionrole, infrastructure_template_yaml_imagebucket, infrastructure_template_yaml_deadletterqueue [EXTRACTED 1.00]

## Communities (26 total, 4 thin omitted)

### Community 0 - "TW Stock Data Sync"
Cohesion: 0.07
Nodes (40): MongoClient, _extract_autocomplete_company_name(), format_total_net_diff(), _format_trade_value(), format_twse_buy_and_sell_result(), get_effective_date(), get_institues_buy_sell_today_result(), get_symbol_buy_sell_today_result() (+32 more)

### Community 1 - "LINE Webhook Handler"
Cohesion: 0.08
Nodes (24): Any, MessagingApi, create_response(), handle_text_message(), lambda_handler(), mark_message_as_read(), Uses the Line SDK's underlying ApiClient to mark a message as read., Create HTTP response for API Gateway      Args:         status_code: HTTP status (+16 more)

### Community 2 - "Fugle Quote & Chart"
Cohesion: 0.25
Nodes (9): _get_api_key(), _get_api_key(), _get_api_secret(), get_futopt_snapshot(), Get a one-shot futures/options snapshot from SinoPac's shioaji API.     Returns, get_ssm_parameter(), Fetches a parameter from AWS SSM Parameter Store, using a cache., generate_gemini_technical_analysis_response() (+1 more)

### Community 3 - "Chart Rendering Shared"
Cohesion: 0.12
Nodes (29): draw_turnover_header(), get_x_label_align(), load_chart_font_name(), Shared chart-rendering helpers used by both the TW (Fugle) and US/foreign (yfina, Register the bundled Noto Sans TC font and return its family name., Render the top-right turnover block: label / number / unit columns, right-aligne, Save the figure locally (dev) or upload to S3 and return a presigned URL (Lambda, save_or_upload_fig() (+21 more)

### Community 4 - "Quote Output Formatting"
Cohesion: 0.13
Nodes (13): format_analysis_output(), format_cash_dividend(), format_ex_dividend_response(), format_price_output(), get_ups_or_downs(), Determine if the stock price is up, down, or unchanged.     Returns 1 for up, -1, Test cases for get_ups_or_downs function, Test when current price is higher than previous close (+5 more)

### Community 5 - "Command Parser Tests"
Cohesion: 0.11
Nodes (10): Test cases for parse_line_command function, Test getting US stock info, Test when Taiwan stock is not found, Test when US stock is not found, Test parsing multiple stocks (like #美股), Test #台指期 returns Taiwan futures index price., Test get_tw_futopt_price returns formatted dict., Test get_tw_futopt_price returns None when snapshot fails. (+2 more)

### Community 6 - "AWS SAM Infrastructure"
Cohesion: 0.13
Nodes (17): line-webhook Lambda, Pharaoh Project Overview, SSM Parameter Store Secrets, sync-tw-data Lambda, TWSE/TPEX Open APIs, DeadLetterQueue (SQS), ImageBucket (S3), LineWebhookApi Gateway (+9 more)

### Community 7 - "Fixed Command Mappings"
Cohesion: 0.16
Nodes (8): get_all_commands(), get_stock_symbol_from_fixed_command(), Test #台指期 command maps to TXFR1 with TW_FUT market type, Test #台積期 command maps to CDFR1 with TW_FUT market type, Test unknown command should return None, Test cases for get_stock_symbol_from_fixed_command function, Test #美股 command returns list of US indices, TestGetStockSymbolFromFixedCommand

### Community 8 - "Project Concepts & Rationale"
Cohesion: 0.14
Nodes (16): Bot Command Grammar, Fugle Data Source, Gemini AI Commentary, Shared Quote Output Normalization, S3 Presigned URL Reply Contract, Shioaji/SinoPac Data Source, Symbol Resolution & Market Routing, yfinance Data Source (+8 more)

### Community 9 - "Interactive REPL & Dispatch"
Cohesion: 0.12
Nodes (10): interactive_test(), Interactive testing of the stock parser, handle_ex_dividend_quote(), parse_line_command(), If text starts with '#', extract the symbol and return it with market type., Test getting Taiwan stock info, Test non-stock commands return None, Test overly long commands are ignored (+2 more)

### Community 10 - "Command Parser Handlers"
Cohesion: 0.26
Nodes (13): format_symbol_buy_sell_response(), get_stock_symbol_and_market_type(), get_tw_futopt_price(), handle_buy_and_sell_quote(), handle_day_k_line(), handle_stock_basic_analysis_quote(), handle_stock_price_quote(), handle_year_k_line() (+5 more)

### Community 11 - "TW Stock Price Fetch Tests"
Cohesion: 0.14
Nodes (9): _fallback_stock_price(), Fallback method using Taiwan Stock Exchange API or web scraping., Test fallback using TWSE API, Test cases for get_tw_stock_price function, Test successful stock price fetch using fugle and yfinance, Test when stock symbol is not found with yfinance, Test fallback method when fugleyfinance fails, Test fallback method when fugleyfinance fails (+1 more)

### Community 12 - "Symbol Resolution Tests"
Cohesion: 0.15
Nodes (7): Test cases for get_stock_symbol_and_marke_type function, Test parsing valid stock symbols starting with #, Test parsing with leading/trailing spaces, Test various invalid formats, Test fixed commands like #大盤, #美股, etc., Test tw company commands like #台積電, #長榮, etc., TestGetStockSymbolAndMarketType

### Community 13 - "NVDA Yearly Chart Image"
Cohesion: 0.18
Nodes (11): NVDA 1-Year Candlestick Chart, Period High 236.26, Period Low 164.08, 20-Day MA 202.12, 5-Day MA 207.61, 60-Day MA 208.85, Current Price 202.81 (-2.21%), NVIDIA Corporation (NVDA) (+3 more)

### Community 14 - "Price Response Format Tests"
Cohesion: 0.22
Nodes (7): format_stock_price_response(), Get icon representation for ups or downs status, Test cases for format_stock_price_response function, Test formatting when price is up, Test formatting when price is down, Test formatting when price is unchanged, TestFormatStockPriceResponse

### Community 15 - "Yahoo Finance Tests"
Cohesion: 0.22
Nodes (5): Test cases for quote_stock function, Test successful stock price fetch using yfinance, Test when stock symbol is not found, Test when yfinance fails, TestQuoteStock

### Community 16 - "NVDA Intraday Chart Image"
Cohesion: 0.25
Nodes (8): NVDA Intraday Chart, Intraday High 206.65, Intraday Low 197.97, Price 202.81 (-4.59, -2.21%), US Session 09:30-16:00, yfinance data source, NVIDIA Corporation (NVDA), Turnover 126.8M

### Community 17 - "OHI Intraday Chart Image"
Cohesion: 0.29
Nodes (7): OHI Intraday Chart, Day High 50.75 / Low 49.71, Intraday Price 50.21 (+0.68%), Data source: yfinance (US intraday), Omega Healthcare Investors (OHI), Trend: morning peak, midday dip, late-day recovery, Trade Turnover 1.5M

### Community 18 - "Deps & Tooling Config"
Cohesion: 0.50
Nodes (4): Ruff Pre-Commit Hooks, Conda Environment Spec (pharaoh), Dev Python Requirements, Lambda Python Requirements

### Community 24 - "fugle.py"
Cohesion: 0.27
Nodes (7): Figure, _build_candles_figure(), get_tw_stock_candles_png(), get_tw_stock_candles_png_bytes(), quote_stock_candles(), quote_stock_ticker(), upload_tw_stock_candles_png_to_s3()

## Knowledge Gaps
- **38 isolated node(s):** `deploy.sh script`, `init.sh script`, `local.sh script`, `graphify`, `Shioaji/SinoPac Data Source` (+33 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `parse_line_command()` connect `Interactive REPL & Dispatch` to `LINE Webhook Handler`, `Command Parser Handlers`, `Command Parser Tests`?**
  _High betweenness centrality (0.103) - this node is a cross-community bridge._
- **Why does `get_stock_symbol_and_market_type()` connect `Command Parser Handlers` to `TW Stock Data Sync`, `Symbol Resolution Tests`, `Fixed Command Mappings`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Why does `get_tw_stock_price()` connect `Command Parser Handlers` to `TW Stock Data Sync`, `TW Stock Price Fetch Tests`, `Chart Rendering Shared`, `Quote Output Formatting`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `parse_line_command()` (e.g. with `interactive_test()` and `handle_text_message()`) actually correct?**
  _`parse_line_command()` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `get_stock_symbol_and_market_type()` (e.g. with `get_tw_stock_symbol_from_company_name()` and `.test_edge_cases()`) actually correct?**
  _`get_stock_symbol_and_market_type()` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `get_tw_stock_price()` (e.g. with `handle_stock_basic_analysis_quote()` and `handle_stock_price_quote()`) actually correct?**
  _`get_tw_stock_price()` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `get_tw_stock_candles_png()` (e.g. with `draw_turnover_header()` and `get_x_label_align()`) actually correct?**
  _`get_tw_stock_candles_png()` has 9 INFERRED edges - model-reasoned connections that need verification._