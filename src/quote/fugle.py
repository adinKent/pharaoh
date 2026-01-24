import logging
import os

from fugle_marketdata import RestClient

from utils.aws_helper import get_ssm_parameter

logger = logging.getLogger(__name__)

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
