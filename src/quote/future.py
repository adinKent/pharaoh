import logging
import yfinance as yf

from quote.output import format_price_output

logger = logging.getLogger(__name__)


def get_future_price(symbol: str) -> dict | None:
    """
    Get real-time stock price for a US stock symbol using yfinance library.
    Returns a dict with price info or None if not found.
    """
    try:
        ticker = yf.Ticker(symbol)
        
        # Get current price info
        info = ticker.info
        history = ticker.history(period="2d")

        if not history.empty and info:
            return format_price_output(symbol, info)
    except Exception as e:
        logger.error(f"Error fetching US stock price with yfinance: {e}")
        logger.exception(e)

    return None
