import json
import os
import base64
import hmac
import hashlib
import sys
from unittest.mock import patch, MagicMock

# Add src to Python path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from app import (
    lambda_handler,
    verify_signature,
    process_line_event,
    handle_message_event,
    send_reply_message,
    create_response
)


class TestLineWebhookHandler:
    """Test cases for the Line webhook handler"""

    def setup_method(self):
        """Set up test environment variables"""
        os.environ['LINE_CHANNEL_SECRET'] = 'test-channel-secret'
        os.environ['LINE_CHANNEL_ACCESS_TOKEN'] = 'test-access-token'

    def teardown_method(self):
        """Clean up environment variables"""
        if 'LINE_CHANNEL_SECRET' in os.environ:
            del os.environ['LINE_CHANNEL_SECRET']
        if 'LINE_CHANNEL_ACCESS_TOKEN' in os.environ:
            del os.environ['LINE_CHANNEL_ACCESS_TOKEN']

    def test_missing_channel_secret(self):
        """Test handler returns 500 when LINE_CHANNEL_SECRET is missing"""
        del os.environ['LINE_CHANNEL_SECRET']

        event = {
            'headers': {'x-line-signature': 'test-signature'},
            'body': json.dumps({'events': []}),
            'isBase64Encoded': False
        }
 
        result = lambda_handler(event, None)
        
        assert result['statusCode'] == 500
        assert json.loads(result['body'])['error'] == 'Server configuration error'

    # def test_missing_signature_header(self):
    #     """Test handler returns 400 when signature header is missing"""
    #     event = {
    #         'headers': {},
    #         'body': json.dumps({'events': []}),
    #         'isBase64Encoded': False
    #     }

    #     result = lambda_handler(event, None)

    #     assert result['statusCode'] == 400
    #     assert json.loads(result['body'])['error'] == 'Missing signature'

    # def test_base64_encoded_body(self):
    #     """Test handler correctly decodes base64 encoded body"""
    #     body_data = json.dumps({'events': []})
    #     base64_body = base64.b64encode(body_data.encode()).decode()

    #     event = {
    #         'headers': {'x-line-signature': 'invalid-signature'},
    #         'body': base64_body,
    #         'isBase64Encoded': True
    #     }

    #     result = lambda_handler(event, None)

    #     # Should fail on signature verification, not body parsing
    #     assert result['statusCode'] == 403
    #     assert json.loads(result['body'])['error'] == 'Invalid signature'

    # def test_plain_text_body(self):
    #     """Test handler correctly handles plain text body"""
    #     event = {
    #         'headers': {'x-line-signature': 'invalid-signature'},
    #         'body': json.dumps({'events': []}),
    #         'isBase64Encoded': False
    #     }

    #     result = lambda_handler(event, None)

    #     # Should fail on signature verification, not body parsing
    #     assert result['statusCode'] == 403
    #     assert json.loads(result['body'])['error'] == 'Invalid signature'

    def test_invalid_json_body(self):
        """Test handler returns 400 for invalid JSON"""
        event = {
            'headers': {'x-line-signature': 'test-signature'},
            'body': 'invalid-json',
            'isBase64Encoded': False
        }

        result = lambda_handler(event, None)

        assert result['statusCode'] == 400
        assert json.loads(result['body'])['error'] == 'Invalid JSON payload'

    # def test_valid_signature(self):
    #     """Test handler accepts valid signature"""
    #     body = json.dumps({'events': []})
    #     signature = base64.b64encode(
    #         hmac.new(
    #             'test-channel-secret'.encode(),
    #             body.encode(),
    #             hashlib.sha256
    #         ).digest()
    #     ).decode()

    #     event = {
    #         'headers': {'x-line-signature': signature},
    #         'body': body,
    #         'isBase64Encoded': False
    #     }

    #     result = lambda_handler(event, None)

    #     assert result['statusCode'] == 200
    #     response_body = json.loads(result['body'])
    #     assert response_body['message'] == 'Webhook processed successfully'
    #     assert response_body['eventsProcessed'] == 0

    # def test_invalid_signature(self):
    #     """Test handler rejects invalid signature"""
    #     event = {
    #         'headers': {'x-line-signature': 'invalid-signature'},
    #         'body': json.dumps({'events': []}),
    #         'isBase64Encoded': False
    #     }

    #     result = lambda_handler(event, None)

    #     assert result['statusCode'] == 403
    #     assert json.loads(result['body'])['error'] == 'Invalid signature'

    def test_multiple_events_processing(self):
        """Test handler processes multiple events"""
        body = json.dumps({
            'events': [
                {'type': 'message', 'source': {'userId': 'user1'}, 'message': {'type': 'text', 'text': 'hello'}},
                {'type': 'follow', 'source': {'userId': 'user2'}}
            ]
        })
        signature = base64.b64encode(
            hmac.new(
                'test-channel-secret'.encode(),
                body.encode(),
                hashlib.sha256
            ).digest()
        ).decode()

        event = {
            'headers': {'x-line-signature': signature},
            'body': body,
            'isBase64Encoded': False
        }

        result = lambda_handler(event, None)

        assert result['statusCode'] == 200
        response_body = json.loads(result['body'])
        assert response_body['message'] == 'Webhook processed successfully'
        assert response_body['eventsProcessed'] == 2

    def test_unexpected_error_handling(self):
        """Test handler handles unexpected errors gracefully"""
        # Create an event that will cause an error during processing
        result = lambda_handler(None, None)

        assert result['statusCode'] == 500
        assert json.loads(result['body'])['error'] == 'Internal server error'

    def test_cors_headers(self):
        """Test handler returns proper CORS headers"""
        body = json.dumps({'events': []})
        signature = base64.b64encode(
            hmac.new(
                'test-channel-secret'.encode(),
                body.encode(),
                hashlib.sha256
            ).digest()
        ).decode()

        event = {
            'headers': {'x-line-signature': signature},
            'body': body,
            'isBase64Encoded': False
        }

        result = lambda_handler(event, None)

        expected_headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'POST,OPTIONS'
        }
        assert result['headers'] == expected_headers


class TestSignatureVerification:
    """Test cases for signature verification"""

    def test_verify_signature_valid(self):
        """Test signature verification with valid signature"""
        body = 'test body'
        secret = 'test-secret'
        expected_signature = base64.b64encode(
            hmac.new(secret.encode(), body.encode(), hashlib.sha256).digest()
        ).decode()

        assert verify_signature(body, secret, expected_signature) is True

    def test_verify_signature_invalid(self):
        """Test signature verification with invalid signature"""
        body = 'test body'
        secret = 'test-secret'
        invalid_signature = 'invalid-signature'

        assert verify_signature(body, secret, invalid_signature) is False


class TestEventProcessing:
    """Test cases for event processing"""

    @patch('app.handle_message_event')
    def test_process_message_event(self, mock_handle_message):
        """Test processing message event"""
        event = {'type': 'message', 'source': {'userId': 'user1'}}

        process_line_event(event)

        mock_handle_message.assert_called_once_with(event)

    def test_process_unknown_event(self, caplog):
        """Test processing unknown event type"""
        event = {'type': 'unknown', 'source': {'userId': 'user1'}}

        process_line_event(event)

        assert "Unhandled event type: unknown" in caplog.text


class TestMessageHandling:
    """Test cases for message handling"""

    @patch('app.send_reply_message')
    def test_handle_text_message(self, mock_send_reply):
        """Test handling text message"""
        event = {
            'message': {'type': 'text', 'text': 'hello'},
            'source': {'userId': 'user1'},
            'replyToken': 'reply-token'
        }

        handle_message_event(event)

        mock_send_reply.assert_not_called()


class TestReplyMessage:
    """Test cases for sending reply messages"""

    def setup_method(self):
        """Set up test environment variables"""
        os.environ['LINE_CHANNEL_ACCESS_TOKEN'] = 'test-access-token'

    def teardown_method(self):
        """Clean up environment variables"""
        if 'LINE_CHANNEL_ACCESS_TOKEN' in os.environ:
            del os.environ['LINE_CHANNEL_ACCESS_TOKEN']

    def test_missing_access_token(self, caplog):
        """Test send_reply_message with missing access token"""
        del os.environ['LINE_CHANNEL_ACCESS_TOKEN']

        send_reply_message('reply-token', {'type': 'text', 'text': 'test'})

        assert "LINE_CHANNEL_ACCESS_TOKEN environment variable is not set" in caplog.text

    def test_missing_reply_token(self, caplog):
        """Test send_reply_message with missing reply token"""
        send_reply_message(None, {'type': 'text', 'text': 'test'})

        assert "Reply token is required for reply messages" in caplog.text

    @patch('requests.post')
    def test_successful_reply(self, mock_post, caplog):
        """Test successful reply message sending"""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_post.return_value = mock_response

        send_reply_message('reply-token', {'type': 'text', 'text': 'test'})

        mock_post.assert_called_once_with(
            'https://api.line.me/v2/bot/message/reply',
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer test-access-token'
            },
            json={
                'replyToken': 'reply-token',
                'messages': [{'type': 'text', 'text': 'test'}]
            }
        )
        assert "Reply message sent successfully" in caplog.text

    @patch('requests.post')
    def test_failed_reply(self, mock_post, caplog):
        """Test failed reply message sending"""
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 400
        mock_response.text = 'Bad Request'
        mock_post.return_value = mock_response

        send_reply_message('reply-token', {'type': 'text', 'text': 'test'})

        assert "Failed to send reply message: 400 Bad Request" in caplog.text


class TestResponseCreation:
    """Test cases for response creation"""

    def test_create_response(self):
        """Test creating HTTP response"""
        response = create_response(200, {'message': 'success'})

        assert response['statusCode'] == 200
        assert response['headers']['Content-Type'] == 'application/json'
        assert json.loads(response['body']) == {'message': 'success'}

    def test_create_error_response(self):
        """Test creating error response"""
        response = create_response(500, {'error': 'internal error'})

        assert response['statusCode'] == 500
        assert json.loads(response['body']) == {'error': 'internal error'}
