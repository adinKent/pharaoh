import io
import logging
import os
from pathlib import Path

import boto3
import matplotlib as mpl
import mplfinance as mpf
import pandas as pd
from fugle_marketdata import RestClient

from utils.aws_helper import get_ssm_parameter

logger = logging.getLogger(__name__)

FONT_PATH = Path(__file__).resolve().parents[1] / "assets" / "fonts" / "NotoSansTC-Regular.ttf"

def _get_api_key() -> str | None:
    api_key = os.environ.get("FUGLE_API_KEY")
    if api_key:
        return api_key

    try:
        return get_ssm_parameter("fugle/api-key")
    except Exception as exc:
        logger.warning("FUGLE_API_KEY is not configured: %s", exc)
        return None


client = RestClient(api_key=_get_api_key())

def quote_stock(symbol: str) -> dict | None:
    try:
        stock = client.stock
        result = stock.intraday.quote(symbol=symbol)

        if not result:
            logger.warning("Fugle responses missing price data for %s", symbol)
            return None

        return result
    except Exception as exc:
        logger.error("Fugle API error for %s: %s", symbol, exc)
        logger.exception(exc)
        return None

def quote_stock_ticker(symbol: str) -> dict | None:
    try:
        stock = client.stock
        result = stock.intraday.ticker(symbol=symbol)

        if not result:
            logger.warning("Fugle responses missing ticker data for %s", symbol)
            return None

        return result
    except Exception as exc:
        logger.error("Fugle API error for %s: %s", symbol, exc)
        logger.exception(exc)
        return None

def quote_stock_candles(symbol: str) -> dict | None:
    try:
        stock = client.stock
        result = stock.intraday.candles(symbol=symbol, timeframe="1")

        if not result:
            logger.warning("Fugle responses missing candles data for %s", symbol)
            return None

        return result
    except Exception as exc:
        logger.error("Fugle API error for %s: %s", symbol, exc)
        logger.exception(exc)
        return None


def _build_candles_figure(
    symbol: str,
    timeframe: str = "1",
    y_min: float | None = None,
    y_max: float | None = None,
    show_previous_close: bool = True,
    tight_x: bool = True,
    show_volume: bool = False,
    volume_color: str = "#8fb3ff",
    line_above_color: str = "#ff4d4d",
    line_below_color: str = "#2ecc71",
    title: str | None = None,
    title_y: float | None = None,
    ytick_rotation: float = 0,
    annotate_high_low: bool = True,
    high_low_color: str = "#ffd166",
) -> mpl.figure.Figure | None:
    if FONT_PATH.exists():
        try:
            mpl.font_manager.fontManager.addfont(str(FONT_PATH))
            mpl.rcParams["font.family"] = "Noto Sans TC"
        except Exception as exc:
            logger.warning("Failed to load font %s: %s", FONT_PATH, exc)

    stock = client.stock
    result = stock.intraday.candles(symbol=symbol, timeframe=timeframe)
    if not result:
        logger.warning("Fugle responses missing candle data for %s", symbol)
        return None

    candles = result.get("data", {}).get("candles", [])
    if not candles:
        logger.warning("Fugle candles response missing data for %s: %s", symbol, result)
        return None

    df = pd.DataFrame(candles)
    if "time" not in df.columns:
        logger.warning("Fugle candles missing time field for %s: %s", symbol, result)
        return None

    df["time"] = pd.to_datetime(df["time"])
    df = df.set_index("time")
    df = df.rename(
        columns={
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume",
        }
    )

    market_colors = mpf.make_marketcolors(
        up="white",
        down="white",
        edge="white",
        wick="white",
        volume=volume_color,
    )
    previous_close = result.get("data", {}).get("previousClose")
    if previous_close is None:
        previous_close = result.get("data", {}).get("priceReference")
    try:
        previous_close = float(previous_close)
    except (TypeError, ValueError):
        previous_close = None

    dark_blue_style = mpf.make_mpf_style(
        base_mpf_style="nightclouds",
        marketcolors=market_colors,
        facecolor="#0b1b3b",
        gridcolor="#1f2f57",
    )
    ylim = None
    if y_min is not None or y_max is not None:
        ylim = (y_min, y_max)
    hlines = None
    if show_previous_close and previous_close is not None:
        hlines = dict(
            hlines=[previous_close],
            colors=["#8fb3ff"],
            linestyle="--",
            linewidths=1,
        )
    addplots = None
    if previous_close is not None:
        close_series = df["Close"]
        above = close_series.where(close_series >= previous_close)
        below = close_series.where(close_series < previous_close)
        addplots = [
            mpf.make_addplot(above, type="line", color=line_above_color, width=1),
            mpf.make_addplot(below, type="line", color=line_below_color, width=1),
        ]
    xlim = None
    if tight_x and not df.empty:
        xlim = (df.index[0], df.index[-1])

    if title is None:
        title = f"{symbol} Intraday"

    fig, _ = mpf.plot(
        df,
        type="line",
        volume=show_volume,
        style=dark_blue_style,
        ylim=ylim,
        xlim=xlim,
        hlines=hlines,
        linecolor="#0b1b3b",
        addplot=addplots,
        returnfig=True,
    )
    if title:
        fig.suptitle(
            title,
            y=0.5 if title_y is None else title_y,
            ha="center",
            va="center",
        )
    for axis in fig.axes:
        axis.tick_params(axis="y", labelrotation=ytick_rotation)
    fig.patch.set_facecolor("#0b1b3b")

    if annotate_high_low and not df.empty:
        ax = fig.axes[0]
        high_idx = df["High"].idxmax()
        high_val = df.loc[high_idx, "High"]
        low_idx = df["Low"].idxmin()
        low_val = df.loc[low_idx, "Low"]
        x_min_current, x_max_current = ax.get_xlim()
        y_min_current, y_max_current = ax.get_ylim()
        y_span = y_max_current - y_min_current
        y_pad = max(y_span * 0.02, 0.01)

        high_text_y = min(high_val + y_pad, y_max_current - y_pad)
        low_text_y = max(low_val - y_pad, y_min_current + y_pad)

        x_span = x_max_current - x_min_current
        x_pad = max(x_span * 0.01, 0.5)
        high_text_x = min(max(high_idx, x_min_current + x_pad), x_max_current - x_pad)
        low_text_x = min(max(low_idx, x_min_current + x_pad), x_max_current - x_pad)

        ax.text(
            high_text_x,
            high_text_y,
            f"H {high_val:.2f}",
            ha="center",
            va="bottom",
            color=high_low_color,
            clip_on=True,
        )
        ax.plot(
            [high_idx, high_text_x],
            [high_val, high_text_y],
            color=high_low_color,
            linewidth=1,
        )
        ax.text(
            low_text_x,
            low_text_y,
            f"L {low_val:.2f}",
            ha="center",
            va="top",
            color=high_low_color,
            clip_on=True,
        )
        ax.plot(
            [low_idx, low_text_x],
            [low_val, low_text_y],
            color=high_low_color,
            linewidth=1,
        )

    return fig


def get_tw_stock_candles_png(
    symbol: str,
    timeframe: str = "1",
    y_min: float | None = None,
    y_max: float | None = None,
    show_previous_close: bool = True,
    tight_x: bool = True,
    show_volume: bool = False,
    volume_color: str = "#8fb3ff",
    line_above_color: str = "#ff4d4d",
    line_below_color: str = "#2ecc71",
    title: str | None = None,
    title_y: float | None = None,
    ytick_rotation: float = 0,
    dpi: int = 200,
    annotate_high_low: bool = True,
    high_low_color: str = "#ffd166",
) -> str | None:
    try:
        project_root = Path(__file__).resolve().parents[2]
        output_path = project_root / f"{symbol}_line.png"
        fig = _build_candles_figure(
            symbol=symbol,
            timeframe=timeframe,
            y_min=y_min,
            y_max=y_max,
            show_previous_close=show_previous_close,
            tight_x=tight_x,
            show_volume=show_volume,
            volume_color=volume_color,
            line_above_color=line_above_color,
            line_below_color=line_below_color,
            title=title,
            title_y=title_y,
            ytick_rotation=ytick_rotation,
            annotate_high_low=annotate_high_low,
            high_low_color=high_low_color,
        )
        if fig is None:
            return None
        fig.tight_layout(pad=0.2)
        fig.savefig(
            str(output_path),
            facecolor=fig.get_facecolor(),
            bbox_inches="tight",
            pad_inches=0.05,
            dpi=dpi,
        )
        return str(output_path)
    except Exception as exc:
        logger.error("Fugle candle chart error for %s: %s", symbol, exc)
        logger.exception(exc)
        return None


def get_tw_stock_candles_png_bytes(
    symbol: str,
    timeframe: str = "1",
    y_min: float | None = None,
    y_max: float | None = None,
    show_previous_close: bool = True,
    tight_x: bool = True,
    show_volume: bool = False,
    volume_color: str = "#8fb3ff",
    line_above_color: str = "#ff4d4d",
    line_below_color: str = "#2ecc71",
    title: str | None = None,
    title_y: float | None = None,
    ytick_rotation: float = 0,
    dpi: int = 200,
    annotate_high_low: bool = True,
    high_low_color: str = "#ffd166",
) -> bytes | None:
    fig = _build_candles_figure(
        symbol=symbol,
        timeframe=timeframe,
        y_min=y_min,
        y_max=y_max,
        show_previous_close=show_previous_close,
        tight_x=tight_x,
        show_volume=show_volume,
        volume_color=volume_color,
        line_above_color=line_above_color,
        line_below_color=line_below_color,
        title=title,
        title_y=title_y,
        ytick_rotation=ytick_rotation,
        annotate_high_low=annotate_high_low,
        high_low_color=high_low_color,
    )
    if fig is None:
        return None

    buffer = io.BytesIO()
    fig.tight_layout(pad=0.2)
    fig.savefig(
        buffer,
        format="png",
        facecolor=fig.get_facecolor(),
        bbox_inches="tight",
        pad_inches=0.05,
        dpi=dpi,
    )
    buffer.seek(0)
    return buffer.getvalue()


def upload_tw_stock_candles_png_to_s3(
    symbol: str,
    bucket: str,
    key: str,
    timeframe: str = "1",
    y_min: float | None = None,
    y_max: float | None = None,
    show_previous_close: bool = True,
    tight_x: bool = True,
    show_volume: bool = False,
    volume_color: str = "#8fb3ff",
    line_above_color: str = "#ff4d4d",
    line_below_color: str = "#2ecc71",
    title: str | None = None,
    title_y: float | None = None,
    ytick_rotation: float = 0,
    dpi: int = 200,
    annotate_high_low: bool = True,
    high_low_color: str = "#ffd166",
) -> str | None:
    png_bytes = get_tw_stock_candles_png_bytes(
        symbol=symbol,
        timeframe=timeframe,
        y_min=y_min,
        y_max=y_max,
        show_previous_close=show_previous_close,
        tight_x=tight_x,
        show_volume=show_volume,
        volume_color=volume_color,
        line_above_color=line_above_color,
        line_below_color=line_below_color,
        title=title,
        title_y=title_y,
        ytick_rotation=ytick_rotation,
        dpi=dpi,
        annotate_high_low=annotate_high_low,
        high_low_color=high_low_color,
    )
    if png_bytes is None:
        return None

    s3 = boto3.client("s3")
    s3.put_object(Bucket=bucket, Key=key, Body=png_bytes, ContentType="image/png")
    return f"s3://{bucket}/{key}"
