import logging
import re
import time

import mplfinance as mpf
import pandas as pd
import yfinance as yf

from quote.chart_common import draw_turnover_header, get_x_label_align, load_chart_font_name, save_or_upload_fig
from quote.chart_theme import get_chart_theme
from quote.output import format_price_output, get_info_for_day_candle_picture
from utils.aws_helper import is_running_on_lambda

logger = logging.getLogger(__name__)


def quote_stock(symbol: str, period: str = "2d") -> dict | None:
    """
    Get real-time stock or index price using yfinance library.
    Returns a dict with price info or None if not found.
    """
    try:
        ticker = yf.Ticker(symbol)

        # Get current price info
        info = ticker.info
        history = ticker.history(period=period)

        if not history.empty and info:
            return format_price_output(symbol, info, history)
    except Exception as e:
        logger.error("Error fetching US stock price with yfinance: %s", e)
        logger.exception(e)

    return None


def _format_volume(volume: float) -> str:
    """Compact share-volume label for US/foreign markets (no 張 lots): K / M / B."""
    for divisor, suffix in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
        if volume >= divisor:
            return f"{volume / divisor:,.1f}{suffix}"
    return f"{volume:,.0f}"


def get_us_stock_candles_png(symbol: str, save_to_local_file: bool | None = None) -> str | None:
    """Intraday line chart for US/foreign symbols (stocks, indices, FX, commodities, crypto).

    Uses yfinance: data-driven y-bounds and x-range (US/foreign markets have no daily price
    limit and their session hours vary), and a volume-only turnover header since 張/億 are
    TW-specific.
    """
    if save_to_local_file is None:
        # On Lambda, upload to S3 (LINE needs a public URL); locally, save a file to inspect.
        save_to_local_file = not is_running_on_lambda()
    try:
        stock_info = quote_stock(symbol)
        if not stock_info:
            return None

        previous_close = stock_info.get("previous_price")
        title_info = get_info_for_day_candle_picture(stock_info)

        df = yf.Ticker(symbol).history(period="1d", interval="1m")
        if df.empty:
            logger.warning("No intraday history found for %s", symbol)
            return None
        df = df[["Open", "High", "Low", "Close", "Volume"]]

        theme = get_chart_theme()
        market_colors = mpf.make_marketcolors(
            up=theme.intraday_mark,
            down=theme.intraday_mark,
            edge=theme.intraday_mark,
            wick=theme.intraday_mark,
            volume=theme.intraday_mark,
        )
        font_name = load_chart_font_name()
        chart_style = mpf.make_mpf_style(
            base_mpf_style=theme.base_mpf_style,
            marketcolors=market_colors,
            facecolor=theme.surface,
            gridcolor=theme.grid,
            rc={"font.family": font_name},
        )

        addplots = []
        if previous_close is not None:
            close_series = df["Close"]
            above = close_series.where(close_series > previous_close)
            equal = close_series.where(close_series == previous_close)
            below = close_series.where(close_series < previous_close)
            if not above.isna().all():
                addplots.append(mpf.make_addplot(above, type="line", color=theme.up, width=1))
            if not equal.isna().all():
                addplots.append(mpf.make_addplot(equal, type="line", color=theme.flat, width=1))
            if not below.isna().all():
                addplots.append(mpf.make_addplot(below, type="line", color=theme.down, width=1))

        high_val = df["High"].max()
        low_val = df["Low"].min()
        # Data-driven bounds (no daily limit); keep the previous-close line in frame.
        y_min = min(low_val, previous_close) if previous_close is not None else low_val
        y_max = max(high_val, previous_close) if previous_close is not None else high_val
        y_pad = max((y_max - y_min) * 0.1, 0.01)
        ylim = (y_min - y_pad, y_max + y_pad)

        has_volume = bool(df["Volume"].sum() > 0)
        fig, axes = mpf.plot(
            df,
            type="line",
            volume=has_volume,
            ylim=ylim,
            addplot=addplots,
            style=chart_style,
            returnfig=True,
            tight_layout=True,
            scale_padding={"left": 0.6, "top": 4, "right": 1, "bottom": 0.6},
        )

        ax = fig.axes[0]
        if previous_close is not None:
            ax.axhline(previous_close, color=theme.flat, linestyle="-", linewidth=0.5)

        # draw labels of highest and lowest price
        x_min_current, x_max_current = ax.get_xlim()
        y_min_current, y_max_current = ax.get_ylim()
        y_span = y_max_current - y_min_current
        y_pad = max(y_span * 0.05, 0.01)
        high_text_y = min(high_val + y_pad, y_max_current - y_pad)
        low_text_y = max(low_val - y_pad, y_min_current + y_pad)

        high_low_value_bbox_style = dict(facecolor=theme.label_box, edgecolor="none", boxstyle="square,pad=0.4")
        (high_x, high_ha) = get_x_label_align(df["High"].argmax(), x_max_current)
        (low_x, low_ha) = get_x_label_align(df["Low"].argmin(), x_max_current)
        ax.text(
            high_x,
            high_text_y,
            f"最高價: {high_val:.2f}",
            ha=high_ha,
            va="center",
            fontsize=10,
            bbox=high_low_value_bbox_style,
            color=theme.ink,
            clip_on=False,
        )
        ax.text(
            low_x,
            low_text_y,
            f"最低價: {low_val:.2f}",
            ha=low_ha,
            va="center",
            fontsize=10,
            bbox=high_low_value_bbox_style,
            color=theme.ink,
            clip_on=False,
        )

        # hide y and volume's label
        ax.yaxis.label.set_visible(False)
        if has_volume:
            axes[2].set_ylabel("")
        for axis in fig.axes:
            axis.tick_params(axis="x", labelrotation=0)

        if title_info:
            fig.suptitle(title_info["title"], x=fig.subplotpars.left - 0.06, ha="left", y=0.97)
            fig.text(0.065, 0.90, title_info["price"], color=title_info["color"], fontsize=12)

        # Volume-only header (張/億 are TW-specific); omit when there's no volume (e.g. indices).
        turnover_rows = []
        total_volume = float(df["Volume"].sum())
        if total_volume > 0:
            turnover_rows.append(("成交", _format_volume(total_volume), "", theme.stat_accent))
        draw_turnover_header(fig, turnover_rows, theme, font_name)

        fig.patch.set_facecolor(theme.surface)
        image_name = f"{re.sub(r'[^A-Za-z0-9]', '_', symbol)}_{round(time.time())}.jpg"
        return save_or_upload_fig(fig, image_name, save_to_local_file)
    except Exception as exc:
        logger.error("Error generating intraday chart for %s: %s", symbol, exc)
        logger.exception(exc)
        return None


def get_us_stock_year_candles_png(symbol: str, save_to_local_file: bool | None = None) -> str | None:
    """6-month daily candlestick chart for US/foreign symbols using yfinance."""
    if save_to_local_file is None:
        # On Lambda, upload to S3 (LINE needs a public URL); locally, save a file to inspect.
        save_to_local_file = not is_running_on_lambda()
    try:
        stock_info = quote_stock(symbol)
        if not stock_info:
            return None

        title_info = get_info_for_day_candle_picture(stock_info)

        df = yf.Ticker(symbol).history(period="6mo")
        if df.empty:
            logger.warning("No 6mo history found for %s", symbol)
            return None

        ma_windows = {"日線(5MA)": 5, "月線(20MA)": 20, "季線(60MA)": 60}
        theme = get_chart_theme()
        ma_colors = {"日線(5MA)": theme.ma5, "月線(20MA)": theme.ma20, "季線(60MA)": theme.ma60}
        ma_series: dict[str, pd.Series] = {name: df["Close"].rolling(window=window, min_periods=window).mean() for name, window in ma_windows.items()}
        ma_addplots = [mpf.make_addplot(ma_series[name], type="line", color=ma_colors[name], width=1.1, panel=0) for name in ma_windows]

        market_colors = mpf.make_marketcolors(
            up=theme.up,
            down=theme.down,
            wick={"up": theme.up, "down": theme.down},
            edge="inherit",
            volume="inherit",
        )
        font_name = load_chart_font_name()
        chart_style = mpf.make_mpf_style(
            base_mpf_style=theme.base_mpf_style,
            marketcolors=market_colors,
            facecolor=theme.surface,
            gridcolor=theme.grid,
            rc={"font.family": font_name},
        )

        y_min_current = df["Low"].min()
        y_max_current = df["High"].max()
        y_pad = max((y_max_current - y_min_current) * 0.1, 0.01)
        new_y_lim = (y_min_current - y_pad, y_max_current + y_pad)

        has_volume = bool(df["Volume"].sum() > 0)
        fig, axes = mpf.plot(
            df,
            type="candle",
            volume=has_volume,
            ylim=new_y_lim,
            addplot=ma_addplots,
            datetime_format="%Y-%m-%d",
            style=chart_style,
            returnfig=True,
            tight_layout=True,
            scale_padding={"left": 0.6, "top": 4, "right": 1, "bottom": 0.6},
        )

        ax = fig.axes[0]
        # Keep MA lines below candlesticks.
        for line in ax.lines:
            line.set_zorder(1)
        for collection in ax.collections:
            collection.set_zorder(2)

        high_val = df["High"].max()
        low_val = df["Low"].min()
        x_min_current, x_max_current = ax.get_xlim()
        low_text_y = low_val - y_pad * 0.7
        high_text_y = high_val + y_pad * 0.7

        high_low_value_bbox_style = dict(facecolor=theme.label_box, edgecolor="none", boxstyle="square,pad=0.4")
        (high_x, high_ha) = get_x_label_align(df["High"].argmax(), x_max_current)
        (low_x, low_ha) = get_x_label_align(df["Low"].argmin(), x_max_current)
        ax.text(
            high_x,
            high_text_y,
            f"最高價: {high_val:.2f}",
            ha=high_ha,
            va="top",
            fontsize=10,
            bbox=high_low_value_bbox_style,
            color=theme.ink,
            clip_on=False,
        )
        ax.text(
            low_x,
            low_text_y,
            f"最低價: {low_val:.2f}",
            ha=low_ha,
            va="bottom",
            fontsize=10,
            bbox=high_low_value_bbox_style,
            color=theme.ink,
            clip_on=False,
        )

        legend_handles = [
            ax.plot([], [], color=ma_colors[name], linewidth=1.2, label=f"{name}: {ma_series[name].dropna().iloc[-1]:.2f}")[0]
            for name in ma_windows
            if not ma_series[name].dropna().empty
        ]
        if legend_handles:
            ax.legend(
                handles=legend_handles,
                loc="upper left",
                fontsize=9,
                frameon=True,
                facecolor=theme.surface,
                edgecolor=theme.grid,
                labelcolor=theme.ink,
            )

        # hide y and volume's label
        ax.yaxis.label.set_visible(False)
        if has_volume:
            axes[2].set_ylabel("")
        for axis in fig.axes:
            axis.tick_params(axis="x", labelrotation=0)

        if title_info:
            fig.suptitle(title_info["title"], x=fig.subplotpars.left - 0.06, ha="left", y=0.97)
            fig.text(0.065, 0.90, title_info["price"], color=title_info["color"], fontsize=12)

        fig.patch.set_facecolor(theme.surface)
        image_name = f"{re.sub(r'[^A-Za-z0-9]', '_', symbol)}_1y_{round(time.time())}.jpg"
        return save_or_upload_fig(fig, image_name, save_to_local_file)
    except Exception as exc:
        logger.error("Error generating 1y candle chart for %s: %s", symbol, exc)
        logger.exception(exc)
        return None
