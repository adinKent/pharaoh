import logging
import yfinance as yf

from quote.output import format_price_output

logger = logging.getLogger(__name__)


def get_index_price(symbol: str, period: str = '2d') -> dict | None:
    """
    Get real-time stock price for a US stock symbol using yfinance library.
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
