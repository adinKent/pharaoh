import re

from quote.tw_stock import get_tw_stock_price, get_tw_stock_symbol_from_company_name
from quote.us_stock import get_us_stock_price


def parse_line_command(command_text: str) -> str | None:
    parsed_result = get_stock_symbol_from_command(command_text)
    if parsed_result:
        if not isinstance(parsed_result, list):
            parsed_result = [parsed_result]

        stock_info_list = []
        for (symbol, market) in parsed_result:
            if market == 'TW':
                stock_info_list.append(get_tw_stock_price(symbol))
            elif market == 'US':
                stock_info_list.append(get_us_stock_price(symbol))

        return "\n ".join(map(lambda stock_info: format_stock_response(stock_info), stock_info_list))
            
    return None


def get_stock_symbol_from_command(command_text: str) -> tuple[str, str] | list[tuple[str, str]] | None:
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

    return None


def get_stock_symbol_from_fixed_command(symbol: str) -> tuple[str, str] | list[tuple[str, str]] | None:
    match symbol:
        case "大盤":
            return ("^TWII", "TW")
        case "美股":
            return [
                ("^GSPC", "US"),
                ("^DJI", "US"),
                ("^IXIC", "US"),
                ("^SOX", "US")
            ]
        case "日股":
            return ("^N225", "US")
        case "韓股":
            return ("^KS11", "US")
        case "亞股":
            return [
                ("^TWII", "TW"),
                ("^N225", "US"),
                ("^KS11", "US")
            ]
        case "美元":
            return ("TWD=X", "US")
        case "日元":
            return ("JPYTWD=X", "US")
        case _:
            return get_tw_stock_symbol_from_company_name(symbol)


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
