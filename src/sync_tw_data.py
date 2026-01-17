import json
import logging
import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import boto3

from src.quote.tw_stock import get_effective_date, sync_all_buy_sell_today_result_to_db

logger = logging.getLogger()
logger.setLevel(logging.INFO)

MIN_SYNC_COUNT = 20000
RETRY_DELAY_MINUTES = 20


def handler(event, context):
    """
    Lambda handler to trigger the synchronization of daily buy/sell data.
    This function is intended to be called by a scheduled event.
    """
    logger.info("Starting daily trade data synchronization job.")
    try:
        matched_count, upserted_count = sync_all_buy_sell_today_result_to_db()
        if matched_count < MIN_SYNC_COUNT:
            effective_date = get_effective_date().strftime("%Y-%m-%d")
            if event.get("retry") == "scheduled" and event.get("retry_for_date") == effective_date:
                return {
                    "statusCode": 422,
                    "body": f"Synchronization data is incomplete: updated_count<{MIN_SYNC_COUNT} (matched_count: {matched_count}, upserted_count: {upserted_count}). Retry already executed for {effective_date}.",
                }
            reason = f"matched_count<{MIN_SYNC_COUNT} ({matched_count})"
            retry_event = {
                "retry": "scheduled",
                "retry_for_date": effective_date,
                "reason": reason,
                "previous_event": event,
            }
            _schedule_retry(context, retry_event)
            return {
                "statusCode": 422,
                "body": f"Synchronization data is incomplete: {reason}. Retry scheduled for {effective_date}.",
            }

        logger.info("Successfully completed daily trade data synchronization job.")
        return {
            "statusCode": 200,
            "body": "Synchronization successful.",
        }
    except Exception as e:
        logger.error("Failed to execute daily trade data synchronization job: %s", e)
        logger.exception(e)
        raise e


def _schedule_retry(context, retry_event):
    role_arn = os.environ.get("SCHEDULER_INVOKE_ROLE_ARN")
    if not role_arn:
        logger.warning("Missing SCHEDULER_INVOKE_ROLE_ARN; retry schedule skipped.")
        return False

    schedule_time = datetime.now(timezone.utc) + timedelta(minutes=RETRY_DELAY_MINUTES)
    schedule_name = f"sync-tw-data-retry-{schedule_time.strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:8]}"
    schedule_expression = f"at({schedule_time.strftime('%Y-%m-%dT%H:%M:%S')})"

    scheduler = boto3.client("scheduler")
    scheduler.create_schedule(
        Name=schedule_name,
        GroupName=os.environ.get("SCHEDULER_GROUP_NAME", "default"),
        ScheduleExpression=schedule_expression,
        FlexibleTimeWindow={"Mode": "OFF"},
        ActionAfterCompletion="DELETE",
        Target={
            "Arn": context.invoked_function_arn,
            "RoleArn": role_arn,
            "Input": json.dumps(retry_event),
        },
    )
    logger.info("Scheduled retry via EventBridge Scheduler: %s at %s", schedule_name, schedule_expression)
    return True
