import json
import os
import hashlib
import hmac
import base64
import logging
import requests

from typing import Dict, Any
from line.command import parse_line_command

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda function to handle Line Messaging API webhooks
    This function receives webhook notifications from Line and processes them
    """
    logger.info(f"Received event: {json.dumps(event, indent=2)}")

    try:
        # Extract headers and body from API Gateway event
        headers = event.get('headers', {})
        body = event.get('body', '')
        is_base64_encoded = event.get('isBase64Encoded', False)
        
        # Decode body if it's base64 encoded
        if is_base64_encoded:
            request_body = base64.b64decode(body).decode('utf-8')
        else:
            request_body = body
        
        # Verify Line signature
        channel_secret = os.environ.get('LINE_CHANNEL_SECRET')
        if not channel_secret:
            logger.error('LINE_CHANNEL_SECRET environment variable is not set')
            return create_response(500, {'error': 'Server configuration error'})
        
        # signature = headers.get('x-line-signature') or headers.get('X-Line-Signature')
        # if not signature:
        #     logger.error('Missing Line signature header')
        #     return create_response(400, {'error': 'Missing signature'})

        # Verify the signature
        # if not verify_signature(request_body, channel_secret, signature):
        #     logger.error('Invalid signature')
        #     return create_response(403, {'error': 'Invalid signature'})

        # Parse the webhook payload
        try:
            webhook_data = json.loads(request_body)
        except json.JSONDecodeError as parse_error:
            logger.error(f'Failed to parse webhook data: {parse_error}')
            return create_response(400, {'error': 'Invalid JSON payload'})

        # Process each event in the webhook
        events = webhook_data.get('events', [])
        logger.info(f"Processing {len(events)} events")

        for line_event in events:
            process_line_event(line_event)

        # Return success response
        return create_response(200, {
            'message': 'Webhook processed successfully',
            'eventsProcessed': len(events)
        })

    except Exception as error:
        logger.error(f'Error processing webhook: {error}')
        return create_response(500, {'error': 'Internal server error'})


def verify_signature(body: str, channel_secret: str, signature: str) -> bool:
    """
    Verify Line webhook signature

    Args:
        body: Request body
        channel_secret: Line channel secret
        signature: Line signature from headers

    Returns:
        True if signature is valid
    """
    hash_value = hmac.new(
        channel_secret.encode('utf-8'),
        body.encode('utf-8'),
        hashlib.sha256
    ).digest()

    expected_signature = base64.b64encode(hash_value).decode('utf-8')
    return signature == expected_signature


def process_line_event(event: Dict[str, Any]) -> None:
    """
    Process individual Line event

    Args:
        event: Line event object
    """
    logger.info(f"Processing event: {json.dumps(event, indent=2)}")

    event_type = event.get('type')
    source = event.get('source', {})
    timestamp = event.get('timestamp')

    if event_type == 'message':
        handle_message_event(event)
    elif event_type == 'follow':
        handle_follow_event(event)
    elif event_type == 'unfollow':
        handle_unfollow_event(event)
    elif event_type == 'join':
        handle_join_event(event)
    elif event_type == 'leave':
        handle_leave_event(event)
    elif event_type == 'memberJoined':
        handle_member_joined_event(event)
    elif event_type == 'memberLeft':
        handle_member_left_event(event)
    elif event_type == 'postback':
        handle_postback_event(event)
    elif event_type == 'beacon':
        handle_beacon_event(event)
    elif event_type == 'accountLink':
        handle_account_link_event(event)
    elif event_type == 'things':
        handle_things_event(event)
    else:
        logger.info(f"Unhandled event type: {event_type}")


def handle_message_event(event: Dict[str, Any]) -> None:
    """
    Handle message events (text, image, video, audio, file, location, sticker)
    """
    message = event.get('message', {})
    source = event.get('source', {})
    reply_token = event.get('replyToken')
    message_type = message.get('type')

    # Get source type and IDs
    source_type = source.get('type')  # 'user', 'group', or 'room'
    group_id = source.get('groupId', '')
    user_id = source.get('userId', '')

    logger.info(f"Received {message_type} message from Source type: {source_type}, user_id: {user_id}, group_id: {group_id}")

    mark_message_as_read_token = message.get('markAsReadToken', None)

    if mark_message_as_read_token:
        mark_message_as_read(mark_message_as_read_token)

    if message_type == 'text':
        text_message = message.get('text')

        try:
            # Try to process stock command
            stock_info = parse_line_command(text_message)

            if stock_info:
                # Format and send stock price response
                logger.info(f"Stock command detected, info: {stock_info}")
                stock_response = format_stock_response(stock_info)
                send_reply_message(reply_token, {
                    'type': 'text',
                    'text': stock_response
                })
            else:
                # Not a stock command, don't reply
                logger.info("No stock command detected.")

        except Exception as e:
            logger.error(f"Error processing stock command: {e}")
            # Don't reply on error to avoid confusing users

    elif message_type == 'image':
        logger.info(f"Image message ID: {message.get('id')}")
        # Handle image message

    elif message_type == 'video':
        logger.info(f"Video message ID: {message.get('id')}")
        # Handle video message

    elif message_type == 'audio':
        logger.info(f"Audio message ID: {message.get('id')}")
        # Handle audio message

    elif message_type == 'file':
        logger.info(f"File message ID: {message.get('id')}")
        # Handle file message

    elif message_type == 'location':
        title = message.get('title')
        address = message.get('address')
        latitude = message.get('latitude')
        longitude = message.get('longitude')
        logger.info(f"Location: {title}, {address} ({latitude}, {longitude})")
        # Handle location message

    elif message_type == 'sticker':
        package_id = message.get('packageId')
        sticker_id = message.get('stickerId')
        logger.info(f"Sticker package: {package_id}, sticker: {sticker_id}")
        # Handle sticker message

    else:
        logger.info(f"Unhandled message type: {message_type}")


def format_stock_response(stock_info) -> str:
    """Get icon representation for ups or downs status"""
    price_diff = stock_info['price'] - stock_info['previous_price']
    price_diff_percent = (price_diff / stock_info['previous_price'] * 100) if stock_info['previous_price'] != 0 else 0
    icon = "➖"  # Unchanged
    price_diff_percent_format = "0"
    if price_diff > 0:
        icon = "📈"  # Up
        price_diff_percent_format = f"+{price_diff_percent:.2f}"
    elif price_diff < 0:
        icon = "📉"  # Down
        price_diff_percent_format = f"{price_diff_percent:.2f}"

    return f"{stock_info['name']} ({stock_info['symbol']}): {stock_info['price']} {icon} {price_diff:.2f} ({price_diff_percent_format}%)"


def handle_follow_event(event: Dict[str, Any]) -> None:
    """
    Handle follow events (when user adds your bot as friend)
    """
    source = event.get('source', {})
    user_id = source.get('userId')

    logger.info(f"User {user_id} followed the bot")

    # You can send a welcome message here
    # Note: Follow events don't have replyToken, use push message instead


def handle_unfollow_event(event: Dict[str, Any]) -> None:
    """
    Handle unfollow events (when user removes your bot)
    """
    source = event.get('source', {})
    user_id = source.get('userId')

    logger.info(f"User {user_id} unfollowed the bot")

    # Clean up user data if needed


def handle_join_event(event: Dict[str, Any]) -> None:
    """
    Handle join events (when bot joins a group or room)
    """
    source = event.get('source', {})
    source_type = source.get('type')
    group_id = source.get('groupId')
    room_id = source.get('roomId')

    logger.info(f"Bot joined {source_type}: {group_id or room_id}")


def handle_leave_event(event: Dict[str, Any]) -> None:
    """
    Handle leave events (when bot leaves a group or room)
    """
    source = event.get('source', {})
    source_type = source.get('type')
    group_id = source.get('groupId')
    room_id = source.get('roomId')

    logger.info(f"Bot left {source_type}: {group_id or room_id}")


def handle_member_joined_event(event: Dict[str, Any]) -> None:
    """
    Handle member joined events
    """
    source = event.get('source', {})
    joined = event.get('joined', {})
    members = joined.get('members', [])

    logger.info(f"Members joined {source.get('type')}: {members}")


def handle_member_left_event(event: Dict[str, Any]) -> None:
    """
    Handle member left events
    """
    source = event.get('source', {})
    left = event.get('left', {})
    members = left.get('members', [])

    logger.info(f"Members left {source.get('type')}: {members}")


def handle_postback_event(event: Dict[str, Any]) -> None:
    """
    Handle postback events (from rich menu, template messages, etc.)
    """
    postback = event.get('postback', {})
    source = event.get('source', {})
    reply_token = event.get('replyToken')

    logger.info(f"Postback data: {postback.get('data')}")

    # Process postback data and respond accordingly


def handle_beacon_event(event: Dict[str, Any]) -> None:
    """
    Handle beacon events
    """
    beacon = event.get('beacon', {})
    source = event.get('source', {})

    logger.info(f"Beacon event: {beacon.get('type')}, hwid: {beacon.get('hwid')}")


def handle_account_link_event(event: Dict[str, Any]) -> None:
    """
    Handle account link events
    """
    link = event.get('link', {})
    source = event.get('source', {})

    logger.info(f"Account link result: {link.get('result')}")


def handle_things_event(event: Dict[str, Any]) -> None:
    """
    Handle LINE Things events
    """
    things = event.get('things', {})
    source = event.get('source', {})

    logger.info(f"Things event: {things.get('type')}, device: {things.get('deviceId')}")


def send_reply_message(reply_token: str, message: Dict[str, Any]) -> None:
    """
    Send reply message to Line

    Args:
        reply_token: Reply token from the event
        message: Message object to send
    """
    access_token = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')

    if not access_token:
        logger.error('LINE_CHANNEL_ACCESS_TOKEN environment variable is not set')
        return

    if not reply_token:
        logger.error('Reply token is required for reply messages')
        return

    try:
        response = requests.post(
            'https://api.line.me/v2/bot/message/reply',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}'
            },
            json={
                'replyToken': reply_token,
                'messages': [message]
            }
        )

        if not response.ok:
            logger.error(f'Failed to send reply message: {response.status_code} {response.text}')
        else:
            logger.info('Reply message sent successfully')

    except Exception as error:
        logger.error(f'Error sending reply message: {error}')


def mark_message_as_read(markAsReadToken: str) -> None:
    """
    Mark messages as read for a specific user

    Args:
        user_id: Line user ID
    """
    access_token = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')

    if not access_token:
        logger.error('LINE_CHANNEL_ACCESS_TOKEN environment variable is not set')
        return

    try:
        response = requests.post(
            'https://api.line.me/v2/bot/chat/markAsRead',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}'
            },
            json={
                'markAsReadToken': markAsReadToken
            }
        )

        if not response.ok:
            logger.error(f'Failed to mark messages as read: {response.status_code} {response.text}')
        else:
            logger.info(f'Messages marked as read for token: {markAsReadToken}')

    except Exception as error:
        logger.error(f'Error marking messages as read: {error}')


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


def get_ups_or_downs_icon(ups_or_downs: int) -> str:
    """Get icon representation for ups or downs status"""
    if ups_or_downs == 1:
        return "📈"  # Up
    elif ups_or_downs == -1:
        return "📉"  # Down
    else:
        return "➖"  # Unchanged
