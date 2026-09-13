# Support stock dividend history command and chart visualization

Introduce the `D{symbol_or_name}` command to query a stock's dividend history over the past 6 years and render a stacked bar chart image response, mirroring the image generation flow of the `P` (intraday price) and `K` (candlestick) commands. The existing `D除息` command is preserved for daily market-wide ex-dividend listings. For historical dividend data, Taiwan stocks retrieve both cash and stock dividend records via FinMind's dividend dataset with a `yfinance` fallback, while US stocks use `yfinance`. Prior years are aggregated into annual totals to reflect long-term trends, while the current year displays individual payout events labeled by ex-dividend date to track ongoing distributions.

## Consequences

- The `D` command prefix transitions from a singleton (`D除息`) to a parameterized stock command family (`D2330`, `D台積電`, `DAAPL`), while backward compatibility for `D除息` is strictly preserved.
- The command parser, routing layer, and natural-language inference catalog must recognize `D` prefix commands for both Taiwan and US equities.
- Dividend visualization adopts the shared `ChartTheme` and font infrastructure, outputting an S3 presigned URL on Lambda or local file in development.
- Taiwan stocks support stacked bars differentiating cash and stock dividends, whereas markets without stock dividends display a single cash series.
- When no dividend records exist across the 6-year window, the system replies with an informative text message rather than generating an empty chart.

