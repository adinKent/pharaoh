FIXED_SYMBOL_NAME_MAPPINGS = {
    "^TWII": "台灣加權指數",
    "^N225": "日經225",
    "^KS11": "韓國KOSPI",
    "GC=F": "黃金",
    "SI=F": "白銀",
    "CL=F": "原油",
    "TWD=X": "USD/TWD",
    "JPYTWD=X": "JPY/TWD"
}


def get_ups_or_downs(current_price, previous_close):
    """
    Determine if the stock price is up, down, or unchanged.
    Returns 1 for up, -1 for down, 0 for unchanged.
    """
    if current_price > previous_close:
        return 1
    elif current_price < previous_close:
        return -1
    else:
        return 0


def format_price_output(symbol:str, stock_info:dict) -> dict:
    current_price = stock_info.get('regularMarketPrice', stock_info.get('currentPrice'))
    previous_close = stock_info.get('regularMarketPreviousClose')
    name = FIXED_SYMBOL_NAME_MAPPINGS.get(symbol)
    if not name:
        name = stock_info.get('shortName', stock_info.get('longName', f'Stock {symbol}'))

    return {
        'symbol': symbol,
        'name': name,
        'price': round(current_price, 2),
        'previous_price': round(previous_close, 2),
        'currency': stock_info.get('currency', 'USD'),
        'time': None,
        'upsOrDowns': get_ups_or_downs(current_price, previous_close)
    }
