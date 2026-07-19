# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Pharaoh is a LINE Messaging API bot that answers stock/market quote commands (Taiwan-focused: TWSE/TPEX stocks, indices, futures, plus US stocks, FX, commodities, crypto). It runs as two container-image Lambdas deployed with AWS SAM:

- `line-webhook` (`src/app.py::lambda_handler`) — API Gateway `/webhook` endpoint; verifies the LINE signature, parses the message as a command, replies with text or a chart image.
- `sync-tw-data` (`src/sync_tw_data.py::handler`) — scheduled weekdays 16:10 Taipei; syncs TWSE/TPEX institutional buy/sell data into MongoDB. If fewer than 20k rows synced, it self-schedules one retry via EventBridge Scheduler.

Note: `README.md` is mostly leftover template boilerplate (generic echo-webhook, DynamoDB examples) — trust the code, not the README, for behavior.

## Commands

```bash
make fmt lint          # ruff format + ruff check --fix (line-length 150)
make test              # python -m pytest tests/ -v
python -m pytest tests/unit/line/test_command_parser.py -v            # one file
python -m pytest tests/unit/line/test_command_parser.py::test_name -v # one test
make package           # sam build
make deploy-dev        # sam build + deploy (also: deploy-staging, deploy-prod)
make local-start       # sam local start-api → http://localhost:3000/webhook
make logs              # tail dev Lambda logs
python interactive_stock_test.py   # REPL to test commands manually (#2330, A台積電, ...)
```

Pre-commit runs ruff check+format. If the hook auto-fixes files, the commit fails — `git add` the fixed files and commit again (don't amend).

## Command grammar (the bot's user interface)

`src/line/command_parser.py::parse_line_command` dispatches on the first character (max 20 chars total, else ignored):

- `#<symbol>` — price quote; `D除息` — today's ex-dividend stocks; `A<symbol>` — technical analysis (moving averages + Gemini AI commentary); `F<symbol>` — institutional buy/sell (from MongoDB); `P<symbol>` — intraday chart PNG; `K<symbol>` — half-year candlestick PNG.

Symbol resolution (`get_stock_symbol_and_market_type`): leading digit → Taiwan stock (`TW`); Chinese characters → fixed command mappings in `src/line/command_mappings.py` (indices, futures, FX, `#指令` help text...), then TWSE company-name lookup; letters → US ticker. Market types route to different quote sources: `TW`/`TW_IND` → Fugle, `TW_FUT` → shioaji, everything else → yfinance. Fixed commands can map to a *list* of symbols (e.g. `美股` → four indices) — handlers must cope with str | tuple | list returns.

Handlers return a plain string; if it's an S3 presigned URL (`is_s3_presigned_url`), `app.py` sends an image reply instead of text. Chart PNGs are uploaded to the image S3 bucket via `utils/aws_helper.py::put_image`. When creating or restyling chart images, follow the `image-response-design` skill (`.claude/skills/image-response-design/SKILL.md`).

## Quote data sources

- **Fugle** (`src/quote/fugle.py`) — TW stock/index intraday quotes, tickers, candle charts. Field names differ from Yahoo (`lastPrice`, `referencePrice`, ...); `get_tw_stock_price` normalizes them into a yfinance-shaped dict before `format_price_output`. Fugle may return keys with `None` values — use `x.get("a") or x.get("b")` fallbacks, not `x.get("a", x.get("b"))`.
- **shioaji / SinoPac** (`src/quote/sinopac.py`) — TW futures snapshots (e.g. `TXFR1`). Imported lazily; sets `HOME=/tmp` on Lambda because shioaji writes a token pool under `$HOME/.shioaji`.
- **yfinance** (`src/quote/yahoo_finance.py`, also history in `tw_stock.py`) — US/international quotes and price history. TW history symbols are `{symbol}.TW` (TWSE) or `{symbol}.TWO` (TPEX).
- **TWSE/TPEX open APIs** (scraped/fetched in `src/quote/tw_stock.py`) — ex-dividend calendar, institutional buy/sell; the latter is synced to MongoDB by `sync_tw_data.py` and read back for `F` commands.
- **Gemini** (`src/utils/gemini_helper.py`) — AI commentary for `A` commands.

`src/quote/output.py` is the shared formatting layer: everything is normalized to a dict with `price`/`previous_price`/`upsOrDowns` etc.; responses are Traditional Chinese.

## Config & secrets

All secrets live in SSM Parameter Store under `/pharaoh/{ENVIRONMENT}/...` (line/channel-secret, fugle/api-key, sinopac/api-key+secret, mongodb/coonnect-str [sic], mongodb/credentials). Accessors check the env var first (`FUGLE_API_KEY`, `SINOPAC_API_KEY`, ...), then fall back to SSM via `utils/aws_helper.py::get_ssm_parameter`. Infra is defined in `infrastructure/template.yaml`; both Lambdas build from the multi-target `infrastructure/Dockerfile`.

## Tests

`tests/unit/` mirrors `src/` (`line/`, `quote/`); external APIs are mocked — tests never hit Fugle/LINE/AWS. `tests/conftest.py` handles the `src` path setup.
