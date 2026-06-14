import logging
import os

from utils.aws_helper import get_ssm_parameter

logger = logging.getLogger(__name__)


def _get_api_key() -> str | None:
    api_key = os.environ.get("SINOPAC_API_KEY")
    if api_key:
        return api_key

    try:
        return get_ssm_parameter("sinopac/api-key")
    except Exception as exc:
        logger.warning("SINOPAC_API_KEY is not configured: %s", exc)
        return None


def _get_api_secret() -> str | None:
    api_secret = os.environ.get("SINOPAC_API_SECRET")
    if api_secret:
        return api_secret

    try:
        return get_ssm_parameter("sinopac/api-secret")
    except Exception as exc:
        logger.warning("SINOPAC_API_SECRET is not configured: %s", exc)
        return None


def get_futopt_snapshot(symbol: str) -> dict | None:
    """
    Get a one-shot futures/options snapshot from SinoPac's shioaji API.
    Returns dict with close, change_price, change_rate, reference_price or None on failure.
    """
    try:
        import shioaji as sj
    except ImportError:
        logger.error("shioaji package is not installed")
        return None

    api_key = _get_api_key()
    api_secret = _get_api_secret()

    if not api_key or not api_secret:
        logger.error("SinoPac API credentials are not configured")
        return None

    # shioaji writes its token pool to $HOME/.shioaji; Lambda has no writable $HOME
    if not os.path.isdir(os.environ.get("HOME", "")):
        os.environ["HOME"] = "/tmp"

    api = None
    try:
        api = sj.Shioaji()
        api.login(api_key=api_key, secret_key=api_secret, subscribe_trade=False)

        contract = api.Contracts.Futures[symbol]
        snapshots = api.snapshots([contract])

        if not snapshots:
            logger.warning("SinoPac snapshot returned no data for %s", symbol)
            return None

        snap = snapshots[0]
        close = float(snap.close)
        change_price = float(snap.change_price)

        return {
            "close": close,
            "change_price": change_price,
            "change_rate": float(snap.change_rate),
            "reference_price": round(close - change_price, 2),
        }
    except Exception as exc:
        logger.error("SinoPac API error for %s: %s", symbol, exc)
        logger.exception(exc)
        return None
    finally:
        if api is not None:
            try:
                api.logout()
            except Exception:
                pass
