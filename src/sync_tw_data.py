import logging
from src.quote.tw_stock import sync_all_buy_sell_today_result_to_db

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    """
    Lambda handler to trigger the synchronization of daily buy/sell data.
    This function is intended to be called by a scheduled event.
    """
    logger.info("Starting daily trade data synchronization job.")
    try:
        sync_all_buy_sell_today_result_to_db()
        logger.info("Successfully completed daily trade data synchronization job.")
        return {
            'statusCode': 200,
            'body': 'Synchronization successful.'
        }
    except Exception as e:
        logger.error("Failed to execute daily trade data synchronization job: %s", e)
        logger.exception(e)
        raise e
