import json
import os
from dataclasses import asdict, dataclass

import boto3


@dataclass(frozen=True)
class FinancialRequestJob:
    request_id: str
    user_id: str
    conversation_id: str
    message: str
    event_id: str | None = None


class MongoRequestStatusStore:
    def __init__(self, database: str = "pharaoh", collection: str = "financial_request_status"):
        self.database = database
        self.collection = collection

    def set_status(self, request_id: str, status: str, *, error: str | None = None) -> None:
        from datetime import UTC, datetime

        from utils.mongo_helper import get_mongo_client

        client = get_mongo_client()
        try:
            client[self.database][self.collection].update_one(
                {"_id": request_id},
                {"$set": {"status": status, "error": error, "updated_at": datetime.now(UTC).isoformat()}},
                upsert=True,
            )
        finally:
            client.close()


def enqueue_financial_request(job: FinancialRequestJob) -> str:
    queue_url = os.environ.get("FINANCIAL_REQUEST_QUEUE_URL")
    if not queue_url:
        raise RuntimeError("FINANCIAL_REQUEST_QUEUE_URL is not configured")
    response = boto3.client("sqs").send_message(QueueUrl=queue_url, MessageBody=json.dumps(asdict(job), ensure_ascii=False))
    return response["MessageId"]
