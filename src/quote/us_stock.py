import yfinance as yf

from quote.common import get_ups_or_downs


def get_us_stock_price(symbol: str):
    """
    Get real-time stock price for a US stock symbol using yfinance library.
    Returns a dict with price info or None if not found.
    """
    try:
        ticker = yf.Ticker(symbol)
        
        # Get current price info
        info = ticker.info
        history = ticker.history(period="1d")

        if not history.empty and info:
            current_price = info.get('regularMarketPrice') or info.get('currentPrice')
            previous_close = info.get('regularMarketPreviousClose')

            return {
                'symbol': symbol,
                'name': info.get('shortName', info.get('longName', f'Stock {symbol}')),
                'price': round(current_price, 2),
                'previous_price': round(previous_close, 2),
                'currency': info.get('currency', 'USD'),
                'time': None,
                'upsOrDowns': get_ups_or_downs(current_price, previous_close)
            }
    except Exception as e:
        print(f"Error fetching US stock price with yfinance: {e}")

    return None
