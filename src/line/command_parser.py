import math
import re

import pandas as pd

from line.command_mappings import get_all_commands
from quote.output import FIXED_SYMBOL_NAME_MAPPINGS, format_ex_dividend_response, format_stock_price_response
from quote.sinopac import get_futopt_snapshot
from quote.tw_stock import (
    get_institues_buy_sell_today_result,
    get_symbol_buy_sell_today_result,
    get_today_ex_dividend_stocks,
    get_tw_index_price,
    get_tw_stock_candles_png,
    get_tw_stock_price,
    get_tw_stock_symbol_from_company_name,
    get_tw_stock_year_candles_png,
)
from quote.yahoo_finance import (
    get_us_stock_candles_png,
    get_us_stock_year_candles_png,
    quote_stock,
)
from utils.groq_helper import generate_groq_technical_analysis_response

MAX_COMMAND_TEXT_LENGTH = 20


def get_tw_futopt_price(symbol: str) -> dict | None:
    result = get_futopt_snapshot(symbol)
    if not result:
        return None

    return {
        "symbol": symbol,
        "name": FIXED_SYMBOL_NAME_MAPPINGS.get(symbol, symbol),
        "price": round(result["close"], 2),
        "previous_price": result["reference_price"],
    }


def parse_line_command(command_text: str) -> str | None:
    """
    If text starts with '#', extract the symbol and return it with market type.
    For Taiwan stocks: #2330, #00930A -> ('2330', 'TW'), ('00930A', 'TW')
    For US stocks: #AAPL -> ('AAPL', 'US')
    Otherwise, return None.
    """
    if len(command_text) > MAX_COMMAND_TEXT_LENGTH:
        return None

    price_qutoe_command_match = re.match(r"^#(.+)", command_text.strip())
    if price_qutoe_command_match:
        return handle_stock_price_quote(price_qutoe_command_match)

    ex_dividend_command_match = re.match(r"^D除息$", command_text.strip())
    if ex_dividend_command_match:
        return handle_ex_dividend_quote()

    basic_analysis_command_match = re.match(r"^A(.+)", command_text.strip())
    if basic_analysis_command_match:
        return handle_stock_basic_analysis_quote(basic_analysis_command_match)

    buy_and_sell_quote_match = re.match(r"^F(.+)", command_text.strip())
    if buy_and_sell_quote_match:
        return handle_buy_and_sell_quote(buy_and_sell_quote_match)

    day_k_line_match = re.match(r"^P(.+)", command_text.strip())
    if day_k_line_match:
        return handle_day_k_line(day_k_line_match)

    year_k_line_match = re.match(r"^K(.+)", command_text.strip())
    if year_k_line_match:
        return handle_year_k_line(year_k_line_match)

    return None


def get_stock_symbol_and_market_type(symbol: str):
    symbol = re.sub(r"\s+", "", symbol)  # remove all whitespace via regex

    # Check if it's a Taiwan stock or US stock
    # Taiwan stocks: start with digits (may contain letters at the end)
    # US stocks: start with letters
    if len(symbol) > 0:
        if symbol[0].isdigit():
            return (symbol, "TW")
        elif bool(re.search(r"[\u4e00-\u9fff]", symbol)):
            stock_symbol_list = get_stock_symbol_from_fixed_command(symbol)
            if stock_symbol_list:
                return stock_symbol_list

            stock_symbol = get_tw_stock_symbol_from_company_name(symbol)
            if stock_symbol:
                return (stock_symbol, "TW")
        elif bool(re.search(r"^[A-Za-z0-9]+", symbol)):
            return (symbol.upper(), "US")

    return None


def get_stock_symbol_from_fixed_command(
    symbol: str,
) -> str | tuple[str, str] | list[tuple[str, str]] | None:
    command_mappings = get_all_commands()
    return command_mappings.get(symbol, None)


def handle_stock_price_quote(symbol_in_command) -> str:
    symbol_name = symbol_in_command.group(1)
    symbol_list = get_stock_symbol_and_market_type(symbol_name)
    if isinstance(symbol_list, str):
        return symbol_list

    if not isinstance(symbol_list, list):
        symbol_list = [symbol_list]

    stock_info_list = []
    for symbol, market_type in symbol_list:
        stock_info = None
        match market_type:
            case "TW":
                stock_info = get_tw_stock_price(symbol)
            case "TW_IND":
                stock_info = get_tw_index_price(symbol)
            case "TW_FUT":
                stock_info = get_tw_futopt_price(symbol)
            case _:
                stock_info = quote_stock(symbol)

        if stock_info:
            stock_info_list.append(stock_info)

    return "\n".join(map(lambda stock_info: format_stock_price_response(stock_info), stock_info_list))


def handle_ex_dividend_quote() -> str:
    ex_dividend_stocks, query_date = get_today_ex_dividend_stocks()
    return format_ex_dividend_response(ex_dividend_stocks, query_date)


def handle_stock_basic_analysis_quote(symbol_in_command) -> str:
    symbol_name = symbol_in_command.group(1)
    symbol_list = get_stock_symbol_and_market_type(symbol_name)
    if isinstance(symbol_list, list):
        symbol_list = symbol_list[0]

    (symbol, market_type) = symbol_list
    stock_info = None
    match market_type:
        case "TW":
            stock_info = get_tw_stock_price(symbol, period="1y")
        case "TW_IND":
            stock_info = get_tw_index_price(symbol, period="1y")
        case _:
            stock_info = quote_stock(symbol, period="1y")

    full_info = stock_info["fullInfo"]
    history = stock_info.get("history")

    # History may be a Fugle-derived frame (TW path) or a yfinance frame (US path);
    # both expose a "Close" column. A partial latest row can be NaN, and the price
    # fallback path may omit history entirely — guard for both. Drop NaN closes so
    # an incomplete latest trading-day row does not invalidate every MA window.
    if isinstance(history, pd.DataFrame) and "Close" in history:
        close_history = history["Close"].dropna()
    else:
        close_history = pd.Series(dtype="float64")

    def _last_ma(window):
        if close_history.empty:
            return float("nan")
        return close_history.rolling(window=window).mean().iloc[-1]

    ma5 = _last_ma(5)
    ma20 = _last_ma(20)
    ma60 = _last_ma(60)
    ma120 = _last_ma(120)
    ma240 = _last_ma(240)

    stock_only_info = []
    if full_info.get("dividendYield", None):
        dividend_yield = round(full_info.get("dividendYield", 0), 1)
        stock_only_info.append(f"殖利率: {dividend_yield}%")

    if full_info.get("trailingPE", None):
        trailing_pe = round(full_info.get("trailingPE", 0), 1)
        stock_only_info.append(f"PE: {trailing_pe}")

    if full_info.get("forwardPE", None):  # forwardPE is not correct by yFinance's query
        forward_pe = round(full_info.get("forwardPE", 0), 1)
        stock_only_info.append(f"ForwardPE: {forward_pe}")

    if len(stock_only_info) > 0:
        stock_only_info = ["  ".join(stock_only_info), ""]

    # Skip any moving average that is NaN (not enough history for that window).
    def _ma_line(pairs):
        return "  ".join(f"{label}: {round(value, 2)}" for label, value in pairs if not math.isnan(value))

    ma_lines = [
        line
        for line in (
            _ma_line((("5日線", ma5), ("月線", ma20))),
            _ma_line((("季線", ma60), ("半年線", ma120), ("年線", ma240))),
        )
        if line
    ]

    technical_analysis_content = "\n".join(
        [
            f"{format_stock_price_response(stock_info)}",
            "",
            *stock_only_info,
            *ma_lines,
        ]
    )

    prompt = technical_analysis_content
    if stock_info["fullInfo"]["exchange"]:
        yahoo_stock_symbol = f"{symbol}.{'TW' if stock_info['fullInfo']['exchange'] == 'TWSE' else 'TWO'}"
        prompt += f"""
            可參考下面網站做基本面分析:
            https://tw.stock.yahoo.com/quote/{yahoo_stock_symbol}/profile
            https://tw.stock.yahoo.com/quote/{yahoo_stock_symbol}/dividend
        """

    ai_analysis_content = generate_groq_technical_analysis_response(prompt)  # generate_gemini_technical_analysis_response(prompt)
    return "\n".join([technical_analysis_content, "", "AI分析:", "", ai_analysis_content])


def format_symbol_buy_sell_response(data: dict) -> str:
    """Formats the buy/sell data into a readable string."""
    if not data:
        return "找不到該股票的買賣超資料。"

    # Helper to format numbers. Assumes values are strings with commas.
    def format_net(value_str: str, always_show_sign: bool = False) -> str:
        num = int(value_str.replace(",", ""))

        sign = ""
        if always_show_sign and num > 0:
            sign = "+"

        return f"{sign}{math.trunc(num / 1000)} 張"

    return "\n".join(
        [
            f"{data.get('date')} 三大法人買賣超:",
            "",
            f"外資買進: {format_net(data.get('foreignBuy', '0'))}",
            f"外資賣出: {format_net(data.get('foreignSell', '0'))}",
            f"外資買賣差額: {format_net(data.get('foreignNet', '0'), always_show_sign=True)}",
            "",
            f"投信買進: {format_net(data.get('investTrustBuy', '0'))}",
            f"投信賣出: {format_net(data.get('investTrustSell', '0'))}",
            f"投信買賣差額: {format_net(data.get('investTrustNet', '0'), always_show_sign=True)}",
            "",
            f"自營商(自行買賣)買進: {format_net(data.get('dealerBuy', '0'))}",
            f"自營商(自行買賣)賣出: {format_net(data.get('dealerSell', '0'))}",
            f"自營商(自行買賣)買賣差額: {format_net(data.get('dealerNet', '0'), always_show_sign=True)}",
            "",
            f"自營商(避險)買進: {format_net(data.get('dealerHedgeBuy', '0'))}",
            f"自營商(避險)賣出: {format_net(data.get('dealerHedgeSell', '0'))}",
            f"自營商(避險)買賣差額: {format_net(data.get('dealerHedgeNet', '0'), always_show_sign=True)}",
            "",
            f"自營商合計買賣差額: {format_net(data.get('dealerTotalNet', '0'), always_show_sign=True)}",
            "",
            f"三大法人合計買賣差額: {format_net(data.get('totalNet', '0'), always_show_sign=True)}",
        ]
    )


def handle_buy_and_sell_quote(symbol_in_command) -> str:
    symbol_name = symbol_in_command.group(1)
    symbol_list = get_stock_symbol_and_market_type(symbol_name)
    if isinstance(symbol_list, list):
        symbol_list = symbol_list[0]

    (symbol, market_type) = symbol_list
    if symbol == "IX0001":
        return get_institues_buy_sell_today_result()

    data = get_symbol_buy_sell_today_result(symbol)
    if data:
        real_time_price_quote = handle_stock_price_quote(symbol_in_command)
        return "\n".join([real_time_price_quote, "", format_symbol_buy_sell_response(data)])


def handle_day_k_line(symbol_in_command) -> str:
    symbol_name = symbol_in_command.group(1)
    symbol_list = get_stock_symbol_and_market_type(symbol_name)
    if isinstance(symbol_list, list):
        (symbol, market_type) = symbol_list[0]
    else:
        (symbol, market_type) = symbol_list

    if market_type in ("TW", "TW_IND"):
        return get_tw_stock_candles_png(symbol)
    return get_us_stock_candles_png(symbol)


def handle_year_k_line(symbol_in_command) -> str:
    symbol_name = symbol_in_command.group(1)
    symbol_list = get_stock_symbol_and_market_type(symbol_name)
    if isinstance(symbol_list, list):
        (symbol, market_type) = symbol_list[0]
    else:
        (symbol, market_type) = symbol_list

    if market_type in ("TW", "TW_IND"):
        return get_tw_stock_year_candles_png(symbol)
    return get_us_stock_year_candles_png(symbol)
