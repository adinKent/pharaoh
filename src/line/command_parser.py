import re

from quote.tw_stock import get_tw_stock_price, get_tw_stock_symbol_from_company_name
from quote.us_stock import get_us_stock_price
from quote.index import get_index_price
from quote.future import get_future_price
from line.command_mappings import get_all_commands
from quote.tw_stock import get_twse_buy_sell_today_result


def parse_line_command(command_text: str) -> str | None:
    """
    If text starts with '#', extract the symbol and return it with market type.
    For Taiwan stocks: #2330, #00930A -> ('2330', 'TW'), ('00930A', 'TW')
    For US stocks: #AAPL -> ('AAPL', 'US')
    Otherwise, return None.
    """
    price_qutoe_command_match = re.match(r'^#(.+)', command_text.strip())
    if price_qutoe_command_match:
        return handle_stock_price_qutoe(price_qutoe_command_match)

    buy_and_sell_quote_match = re.match(r'^F(.+)', command_text.strip())
    if buy_and_sell_quote_match:
        symbol = buy_and_sell_quote_match.group(1)
        symbol = re.sub(r"\s+", "", symbol)   # remove all whitespace via regex
        if symbol == "大盤":
            return get_twse_buy_sell_today_result()

    basic_analysis_command_match = re.match(r'^A(.+)', command_text.strip())
    if basic_analysis_command_match:
        return handle_stock_basic_analysis_qutoe(basic_analysis_command_match)

    return None


def get_stock_symbol_and_market_type(symbol:str):
    symbol = re.sub(r"\s+", "", symbol)   # remove all whitespace via regex
    
    # Check if it's a Taiwan stock or US stock
    # Taiwan stocks: start with digits (may contain letters at the end)
    # US stocks: start with letters
    if len(symbol) > 0:
        if symbol[0].isdigit():
            return (symbol, 'TW')
        elif bool(re.search(r'[\u4e00-\u9fff]', symbol)):
            return get_stock_symbol_from_fixed_command(symbol)
        elif bool(re.search(r'^[A-Za-z0-9]+', symbol)):
            return (symbol.upper(), 'US')
    
    return None


def get_stock_symbol_from_fixed_command(symbol: str) -> str | tuple[str, str] | list[tuple[str, str]] | None:
    command_mappings = get_all_commands()
    result = command_mappings.get(symbol, None)
    
    if not result:
        result = get_tw_stock_symbol_from_company_name(symbol)
        if result:
            result = (result, "TW")

    return result


def handle_stock_price_qutoe(symbol_in_command) -> str:
    symbol_name = symbol_in_command.group(1)
    symbol_list = get_stock_symbol_and_market_type(symbol_name)
    if not isinstance(symbol_list, list):
        symbol_list = [symbol_list]

    stock_info_list = []
    for (symbol, market_type) in symbol_list:
        stock_info = None
        match market_type:
            case 'TW':
                stock_info = get_tw_stock_price(symbol)
            case 'US':
                stock_info = get_us_stock_price(symbol)
            case 'IND':
                stock_info = get_index_price(symbol)
            case 'FUT':
                stock_info = get_future_price(symbol)
            case _:
                stock_info = get_us_stock_price(symbol)

        if stock_info:
            stock_info_list.append(stock_info)

    return "\n".join(map(lambda stock_info: format_stock_price_response(stock_info), stock_info_list))


def format_stock_price_response(stock_info) -> str:
    """Get icon representation for ups or downs status"""
    price_diff = stock_info['price'] - stock_info['previous_price']
    price_diff_percent = (price_diff / stock_info['previous_price'] * 100) if stock_info['previous_price'] != 0 else 0
    icon = "➖"  # Unchanged
    price_diff_percent_format = "0"
    if price_diff > 0:
        icon = "📈"  # Up
        price_diff_percent_format = f"+{price_diff_percent:.2f}"
    elif price_diff < 0:
        icon = "📉"  # Down
        price_diff_percent_format = f"{price_diff_percent:.2f}"

    return f"{stock_info['name']} ({stock_info['symbol']}): {stock_info['price']} {icon} {price_diff:.2f} ({price_diff_percent_format}%)"


def handle_stock_basic_analysis_qutoe(symbol_in_command) -> str:
    symbol_name = symbol_in_command.group(1)
    symbol_list = get_stock_symbol_and_market_type(symbol_name)
    if isinstance(symbol_list, list):
        symbol_list = symbol_list[0]

    (symbol, market_type) = symbol_list
    stock_info = None
    match market_type:
        case 'TW':
            stock_info = get_tw_stock_price(symbol, period='1y')
        case 'US':
            stock_info = get_us_stock_price(symbol, period='1y')
        case 'IND':
            stock_info = get_index_price(symbol, period='1y')
        case 'FUT':
            stock_info = get_future_price(symbol, period='1y')
        case _:
            stock_info = get_us_stock_price(symbol, period='1y')

    full_info = stock_info['fullInfo']
    history = stock_info['history']
    
    ma5 = history['Close'].rolling(window=5).mean().iloc[-1]
    ma20 = history['Close'].rolling(window=20).mean().iloc[-1]
    ma60 = history['Close'].rolling(window=60).mean().iloc[-1]
    ma120 = history['Close'].rolling(window=120).mean().iloc[-1]
    ma240 = history['Close'].rolling(window=240).mean().iloc[-1]

    stock_only_info = []
    if full_info.get('dividendYield', None):
        dividend_yield = round(full_info.get('dividendYield', 0), 1)
        stock_only_info.append(f'殖利率: {dividend_yield}%')
    
    if full_info.get('trailingPE', None):
        trailing_pe = round(full_info.get('trailingPE', 0), 1)
        stock_only_info.append(f'PE: {trailing_pe}')

    if full_info.get('forwardPE', None):
        forward_pe = round(full_info.get('forwardPE', 0), 1)
        stock_only_info.append(f'ForwardPE: {forward_pe}')

    if len(stock_only_info) > 0:
        stock_only_info = ["  ".join(stock_only_info), ""]

    return "\n".join([
        f'{format_stock_price_response(stock_info)}', '',
        *stock_only_info,
        f'5日線: {round(ma5, 2)}  月線: {round(ma20, 2)}',
        f'季線: {round(ma60, 2)}  半年線: {round(ma120, 2)}  年線: {round(ma240, 2)}'
    ])
