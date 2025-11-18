import re

from quote.tw_stock import get_tw_stock_price, get_tw_stock_symbol_from_company_name
from quote.us_stock import get_us_stock_price
from quote.index import get_index_price
from quote.future import get_future_price
from line.command_mappings import get_all_commands
from quote.tw_stock import get_twse_fund_today_result


def parse_line_command(command_text: str) -> str | None:
    parsed_result = get_stock_symbol_from_command(command_text)
    if parsed_result:
        if isinstance(parsed_result, str):
            return parsed_result

        if not isinstance(parsed_result, list):
            parsed_result = [parsed_result]

        stock_info_list = []
        for (symbol, market_type) in parsed_result:
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

        return "\n".join(map(lambda stock_info: format_stock_response(stock_info), stock_info_list))
            
    return None


def get_stock_symbol_from_command(command_text: str) -> str | tuple[str, str] | list[tuple[str, str]] | None:
    """
    If text starts with '#', extract the symbol and return it with market type.
    For Taiwan stocks: #2330, #00930A -> ('2330', 'TW'), ('00930A', 'TW')
    For US stocks: #AAPL -> ('AAPL', 'US')
    Otherwise, return None.
    """
    match = re.match(r'^#(.+)', command_text.strip())
    if match:
        symbol = match.group(1)
        symbol = re.sub(r"\s+", "", symbol)   # remove all whitespace via regex
        # Check if it's a Taiwan stock or US stock
        # Taiwan stocks: start with digits (may contain letters at the end)
        # US stocks: start with letters
        if symbol[0].isdigit():
            return (symbol, 'TW')
        elif bool(re.search(r'[\u4e00-\u9fff]', symbol)):
            return get_stock_symbol_from_fixed_command(symbol)
        elif bool(re.search(r'^[A-Za-z0-9]+', symbol)):
            return (symbol.upper(), 'US')

    other_match = re.match(r'^F(.+)', command_text.strip())
    if other_match:
        symbol = other_match.group(1)
        symbol = re.sub(r"\s+", "", symbol)   # remove all whitespace via regex
        if symbol == "大盤":
            return get_twse_fund_today_result()

    return None


def get_stock_symbol_from_fixed_command(symbol: str) -> str | tuple[str, str] | list[tuple[str, str]] | None:
    command_mappings = get_all_commands()
    result = command_mappings.get(symbol, None)
    
    if not result:
        result = get_tw_stock_symbol_from_company_name(symbol)
        if result:
            result = (result, "TW")

    return result


def format_stock_response(stock_info) -> str:
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
