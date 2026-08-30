import json
from unittest.mock import patch

from routing.async_requests import FinancialRequestJob, enqueue_financial_request


def test_enqueue_serializes_request_job(monkeypatch):
    monkeypatch.setenv("FINANCIAL_REQUEST_QUEUE_URL", "https://sqs.example/queue")
    job = FinancialRequestJob("r1", "u1", "c1", "AAPL price", "e1")

    with patch("routing.async_requests.boto3.client") as client_factory:
        client_factory.return_value.send_message.return_value = {"MessageId": "m1"}
        result = enqueue_financial_request(job)

    assert result == "m1"
    body = client_factory.return_value.send_message.call_args.kwargs["MessageBody"]
    assert json.loads(body)["request_id"] == "r1"
