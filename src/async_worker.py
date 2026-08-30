import json
import logging

from linebot.v3.messaging import ApiClient, Configuration, MessagingApi, PushMessageRequest, TextMessage

from routing.async_requests import FinancialRequestJob, MongoRequestStatusStore
from routing.executor import FinancialExecutor
from routing.idempotency import MongoIdempotencyStore
from routing.models import FinancialContext
from routing.router import FinancialRouter

logger = logging.getLogger(__name__)
router = FinancialRouter()
executor = FinancialExecutor()
idempotency = MongoIdempotencyStore()
request_status = MongoRequestStatusStore()


def lambda_handler(event, context):
    access_token = __import__("os").environ.get("LINE_CHANNEL_ACCESS_TOKEN", "")
    api = MessagingApi(ApiClient(Configuration(access_token=access_token)))
    for record in event.get("Records", []):
        job = FinancialRequestJob(**json.loads(record["body"]))
        if not idempotency.claim(job.event_id or job.request_id):
            logger.info("financial_request_duplicate", extra={"request_id": job.request_id, "event_id": job.event_id})
            continue
        request_status.set_status(job.request_id, "processing")
        plan = __import__("asyncio").run(
            router.route(FinancialContext(user_id=job.user_id, message=job.message, conversation_id=job.conversation_id))
        )
        answer = executor.execute(plan, query=job.message)
        api.push_message(PushMessageRequest(to=job.user_id, messages=[TextMessage(text=answer)]))
        request_status.set_status(job.request_id, "completed")
        logger.info("financial_request_completed", extra={"request_id": job.request_id, "event_id": job.event_id})
    return {"processed": len(event.get("Records", []))}
