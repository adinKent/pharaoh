import re

from quote.tw_stock import get_tw_stock_price, get_tw_stock_symbol_from_company_name
from quote.us_stock import get_us_stock_price


def parse_line_command(text: str):
    parsed_result = get_stock_symbol_from_command(text)
    if parsed_result:
        symbol, market = parsed_result
        
        if market == 'TW':
            price_info = get_tw_stock_price(symbol)
        elif market == 'US':
            price_info = get_us_stock_price(symbol)
        else:
            price_info = None
        
        return price_info
    return None


def get_stock_symbol_from_command(text: str):
    """
    If text starts with '#', extract the symbol and return it with market type.
    For Taiwan stocks: #2330, #00930A -> ('2330', 'TW'), ('00930A', 'TW')
    For US stocks: #AAPL -> ('AAPL', 'US')
    Otherwise, return None.
    """
    if text == "#大盤":
        return ("^TWII", "TW")
    
    match = re.match(r'^#(.+)', text.strip())
    if match:
        symbol = match.group(1)
        symbol = re.sub(r"\s+", "", symbol)   # remove all whitespace via regex
        # Check if it's a Taiwan stock or US stock
        # Taiwan stocks: start with digits (may contain letters at the end)
        # US stocks: start with letters
        if symbol[0].isdigit():
            return (symbol, 'TW')
        elif bool(re.search(r'[\u4e00-\u9fff]', symbol)):
            symbol = get_tw_stock_symbol_from_company_name(symbol)
            if symbol:
                return (symbol, 'TW')
        elif bool(re.search(r'^[A-Za-z0-9]+', symbol)):
            return (symbol.upper(), 'US')

    return None
