import json
import os
import logging

from typing import Dict, Any
from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    MarkMessagesAsReadByTokenRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)
from line.command_parser import parse_line_command

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

channel_secret = os.environ.get('LINE_CHANNEL_SECRET')
access_token = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')

if channel_secret is None or access_token is None:
    logger.error('Line channel environment variable is not set correctly at module level')

handler = WebhookHandler(channel_secret or 'default-secret')
configuration = Configuration(access_token=access_token or 'default-token')
api_client = ApiClient(configuration)
line_bot_api = MessagingApi(api_client)


@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    """Handles incoming text messages."""
    try:
        text = event.message.text
        reply_token = event.reply_token

        if event.message.mark_as_read_token:
            mark_message_as_read(line_bot_api, event.message.mark_as_read_token)

        response_text = parse_line_command(text)
        if response_text:
            send_reply_message(line_bot_api, reply_token, response_text)
        else:
            logger.info("No quote command is detected, not to reply.")
    except Exception as e:
        logger.error("Error processing command: %s", e)
        logger.exception(e)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda function to handle Line Messaging API webhooks.
    """
    logger.info("Received event: %s", json.dumps(event, indent=2))
    try:
        headers = event.get('headers', {})
        signature = headers.get('x-line-signature') or headers.get('X-Line-Signature')
        body = event.get('body', '')
        handler.handle(body, signature)
        return create_response(200, {'message': 'Webhook processed successfully'})
    except InvalidSignatureError:
        logger.error("Invalid signature. Please check your channel secret.")
        return create_response(400, {'error': 'Invalid signature'})
    except Exception as error:
        logger.error("Error processing webhook: %s", error)
        logger.exception(error)
        return create_response(500, {'error': 'Internal server error'})


def send_reply_message(message_api: MessagingApi, reply_token: str, text: str) -> None:
    """Uses the Line SDK to send a reply message."""
    try:
        message_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text=text)]
            )
        )
        logger.info("Send reply message successfully.")
    except Exception as e:
        logger.error("Failed to reply message: %s", e)


def mark_message_as_read(message_api: MessagingApi, mark_as_read_token: str) -> None:
    """Uses the Line SDK's underlying ApiClient to mark a message as read."""
    # The v3 SDK doesn't have a high-level method for this specific action yet.
    # The correct approach is to use the underlying client to make the API call.
    try:
        message_api.mark_messages_as_read_by_token(
            MarkMessagesAsReadByTokenRequest(
                mark_as_read_token=mark_as_read_token
            )
        )
        logger.info("Mark message as read successfully.")
    except Exception as e:
        logger.error("Failed to mark message as read: %s", e)


def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create HTTP response for API Gateway

    Args:
        status_code: HTTP status code
        body: Response body

    Returns:
        API Gateway response object
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'POST,OPTIONS'
        },
        'body': json.dumps(body)
    }
