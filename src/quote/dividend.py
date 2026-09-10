import logging
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import matplotlib.pyplot as plt
import pandas as pd
import requests
import yfinance as yf

from quote.chart_common import load_chart_font_name, save_or_upload_fig
from quote.chart_theme import get_chart_theme
from quote.output import FIXED_SYMBOL_NAME_MAPPINGS
from quote.tw_stock import get_tw_stock_price
from quote.yahoo_finance import quote_stock
from utils.aws_helper import is_running_on_lambda

logger = logging.getLogger(__name__)

# Ensure yfinance cache is dummied out on Lambda to prevent SQLite WAL issues
try:
    import yfinance.cache as _yf_cache

    _yf_cache._CookieCacheManager._cookie_cache = _yf_cache._CookieCacheDummy()
    _yf_cache._TzCacheManager._tz_cache = _yf_cache._TzCacheDummy()
    _yf_cache._ISINCacheManager._isin_cache = _yf_cache._ISINCacheDummy()
except Exception:
    pass

FINMIND_API_URL = "https://api.finmindtrade.com/api/v4/data"


def fetch_tw_stock_dividends_finmind(symbol: str, start_year: int) -> list[dict]:
    """Fetch dividend policy history from FinMind API for Taiwan stocks."""
    try:
        params = {
            "dataset": "TaiwanStockDividend",
            "data_id": symbol,
            "start_date": f"{start_year}-01-01",
        }
        resp = requests.get(FINMIND_API_URL, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json().get("data", [])
            records = []
            for row in data:
                date_str = row.get("date")
                if not date_str:
                    continue
                cash = float(row.get("CashEarningsDistribution", 0) or 0) + float(row.get("CashStatutorySurplus", 0) or 0)
                stock = float(row.get("StockEarningsDistribution", 0) or 0) + float(row.get("StockStatutorySurplus", 0) or 0)
                if cash > 0 or stock > 0:
                    records.append(
                        {
                            "date": date_str,
                            "cash": cash,
                            "stock": stock,
                        }
                    )
            return records
    except Exception as exc:
        logger.warning("FinMind dividend fetch failed for %s: %s", symbol, exc)

    return []


def fetch_dividends_yfinance(symbol: str, market_type: str, start_year: int) -> list[dict]:
    """Fetch dividend history from yfinance as primary (US) or fallback (TW)."""
    try:
        yf_symbol = symbol
        if market_type in ("TW", "TW_IND") and not (symbol.endswith(".TW") or symbol.endswith(".TWO")):
            # Try .TW first, then .TWO
            ticker = yf.Ticker(f"{symbol}.TW")
            divs = ticker.dividends
            if divs.empty:
                ticker = yf.Ticker(f"{symbol}.TWO")
                divs = ticker.dividends
        else:
            ticker = yf.Ticker(yf_symbol)
            divs = ticker.dividends

        if divs is None or divs.empty:
            return []

        start_date = pd.Timestamp(f"{start_year}-01-01", tz=divs.index.tz) if divs.index.tz else pd.Timestamp(f"{start_year}-01-01")
        divs = divs[divs.index >= start_date]

        records = []
        for dt, amount in divs.items():
            amt = float(amount)
            if amt > 0:
                records.append(
                    {
                        "date": dt.strftime("%Y-%m-%d"),
                        "cash": amt,
                        "stock": 0.0,
                    }
                )
        return records
    except Exception as exc:
        logger.error("yfinance dividend fetch failed for %s: %s", symbol, exc)
        return []


def aggregate_dividend_records(records: list[dict], current_year: int, start_year: int) -> list[dict]:
    """Aggregate records: past 5 years into annual sums, current year into individual payouts."""
    if not records:
        return []

    # Filter records within [start_year, current_year]
    valid_records = []
    for r in records:
        try:
            year = int(r["date"][:4])
            if start_year <= year <= current_year:
                valid_records.append(r)
        except (ValueError, TypeError, IndexError):
            continue

    if not valid_records:
        return []

    # Sort chronologically by date
    valid_records.sort(key=lambda r: r["date"])

    aggregated = []

    # 1. Past years: group by year
    for yr in range(start_year, current_year):
        yr_records = [r for r in valid_records if int(r["date"][:4]) == yr]
        if yr_records:
            cash_sum = sum(r["cash"] for r in yr_records)
            stock_sum = sum(r["stock"] for r in yr_records)
            aggregated.append(
                {
                    "label": str(yr),
                    "cash": round(cash_sum, 2),
                    "stock": round(stock_sum, 2),
                    "is_current_year": False,
                }
            )

    # 2. Current year: each payout kept individual, labeled by MM/DD
    curr_records = [r for r in valid_records if int(r["date"][:4]) == current_year]
    # Deduplicate / group if multiple events share exact same date
    curr_grouped: dict[str, dict] = {}
    for r in curr_records:
        dt_str = r["date"][:10]
        try:
            label = datetime.strptime(dt_str, "%Y-%m-%d").strftime("%m/%d")
        except ValueError:
            label = dt_str[5:]
        if label not in curr_grouped:
            curr_grouped[label] = {"label": label, "cash": 0.0, "stock": 0.0, "is_current_year": True}
        curr_grouped[label]["cash"] += r["cash"]
        curr_grouped[label]["stock"] += r["stock"]

    for item in curr_grouped.values():
        item["cash"] = round(item["cash"], 2)
        item["stock"] = round(item["stock"], 2)
        aggregated.append(item)

    return aggregated


def fetch_stock_header_info(symbol: str, market_type: str, records: list[dict]) -> dict:
    """Retrieve stock name, price, dividend yield, and TTM cash dividend for the banner."""
    name = FIXED_SYMBOL_NAME_MAPPINGS.get(symbol, symbol)
    current_price = None
    div_yield_pct = None

    if market_type in ("TW", "TW_IND"):
        tw_info = get_tw_stock_price(symbol)
        if tw_info:
            name = tw_info.get("name") or name
            current_price = tw_info.get("price")
    else:
        us_info = quote_stock(symbol)
        if us_info:
            name = us_info.get("name") or name
            current_price = us_info.get("price")

    # Calculate TTM cash dividend (last 365 days)
    now = datetime.now()
    one_year_ago = (now - timedelta(days=365)).strftime("%Y-%m-%d")
    ttm_cash = 0.0
    for r in records:
        if r.get("date", "") >= one_year_ago:
            ttm_cash += r.get("cash", 0.0)

    if current_price and current_price > 0 and ttm_cash > 0:
        div_yield_pct = round((ttm_cash / current_price) * 100, 2)

    return {
        "symbol": symbol,
        "name": name,
        "price": current_price,
        "yield_pct": div_yield_pct,
        "ttm_cash": round(ttm_cash, 2),
    }


def generate_dividend_chart_png(symbol: str, market_type: str, save_to_local_file: bool | None = None) -> str | None:
    """Fetch dividend data, aggregate records, render stacked bar chart, and return image URL/path."""
    if save_to_local_file is None:
        save_to_local_file = not is_running_on_lambda()

    current_year = datetime.now(ZoneInfo("Asia/Taipei")).year
    start_year = current_year - 5  # 6-year window

    # 1. Fetch raw dividend records
    records = []
    if market_type in ("TW", "TW_IND"):
        records = fetch_tw_stock_dividends_finmind(symbol, start_year)
        if not records:
            records = fetch_dividends_yfinance(symbol, market_type, start_year)
    else:
        records = fetch_dividends_yfinance(symbol, market_type, start_year)

    if not records:
        return None

    # 2. Aggregate records
    aggregated = aggregate_dividend_records(records, current_year, start_year)
    if not aggregated:
        return None

    # 3. Header info
    header = fetch_stock_header_info(symbol, market_type, records)

    # 4. Render chart with matplotlib
    theme = get_chart_theme()
    font_name = load_chart_font_name()

    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)
    fig.patch.set_facecolor(theme.surface)
    ax.set_facecolor(theme.surface)

    labels = [item["label"] for item in aggregated]
    cash_vals = [item["cash"] for item in aggregated]
    stock_vals = [item["stock"] for item in aggregated]
    has_stock = any(s > 0 for s in stock_vals)

    x_indices = list(range(len(labels)))
    bar_width = 0.52

    # Color tokens
    cash_color = theme.stat_accent if hasattr(theme, "stat_accent") else "#3a6fd8"
    stock_color = theme.ma5 if hasattr(theme, "ma5") else "#f5a623"

    p1 = ax.bar(x_indices, cash_vals, width=bar_width, color=cash_color, label="現金股利", zorder=3)
    p2 = None
    if has_stock:
        p2 = ax.bar(x_indices, stock_vals, width=bar_width, bottom=cash_vals, color=stock_color, label="股票股利", zorder=3)

    # Value annotations on top of bars
    max_total = 0.0
    for idx, (c, s) in enumerate(zip(cash_vals, stock_vals)):
        total = c + s
        if total > max_total:
            max_total = total

        label_text = ""
        if s > 0 and c > 0:
            label_text = f"{c:g}+{s:g}"
        elif c > 0:
            label_text = f"{c:g}"
        elif s > 0:
            label_text = f"{s:g}股"

        if label_text:
            ax.text(
                idx,
                total + (max_total * 0.02 if max_total > 0 else 0.05),
                label_text,
                ha="center",
                va="bottom",
                fontfamily=font_name,
                fontsize=10,
                fontweight="bold",
                color=theme.ink,
                zorder=4,
            )

    # Styling Axes
    ax.set_xticks(x_indices)
    ax.set_xticklabels(labels, fontfamily=font_name, fontsize=11, color=theme.ink)
    ax.tick_params(axis="x", colors=theme.ink)
    ax.tick_params(axis="y", colors=theme.ink)
    for label in ax.get_yticklabels():
        label.set_fontfamily(font_name)
        label.set_color(theme.ink)

    ax.grid(axis="y", color=theme.grid, linestyle="--", alpha=0.6, zorder=1)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(theme.grid)
    ax.spines["bottom"].set_color(theme.grid)

    # Expand y-limit slightly for value labels
    if max_total > 0:
        ax.set_ylim(0, max_total * 1.2)

    # Title and Subtitle Header
    title_text = f"{header['name']} ({header['symbol']}) 歷年股利走勢"
    fig.text(0.08, 0.94, title_text, fontfamily=font_name, fontsize=15, fontweight="bold", color=theme.ink)

    stats_items = []
    if header.get("price") is not None:
        stats_items.append(f"現價: {header['price']:.2f}")
    if header.get("yield_pct") is not None:
        stats_items.append(f"現金殖利率: {header['yield_pct']:.2f}%")
    if header.get("ttm_cash") is not None and header["ttm_cash"] > 0:
        currency = "元" if market_type in ("TW", "TW_IND") else "$"
        stats_items.append(f"近一年現金股利: {header['ttm_cash']:.2f}{currency}")

    if stats_items:
        stats_text = "   |   ".join(stats_items)
        fig.text(0.08, 0.88, stats_text, fontfamily=font_name, fontsize=11, color=theme.stat_label)

    # Legend if stock dividend is present
    if has_stock:
        ax.legend(
            loc="upper right",
            framealpha=0.4,
            facecolor=theme.surface,
            edgecolor=theme.grid,
            prop={"family": font_name, "size": 10},
            labelcolor=theme.ink,
        )

    plt.subplots_adjust(top=0.83, bottom=0.12, left=0.08, right=0.95)

    try:
        return save_or_upload_fig(fig, f"{symbol}_dividend_{round(time.time())}.jpg", save_to_local_file)
    finally:
        plt.close(fig)
