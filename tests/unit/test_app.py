import json
import os
from unittest.mock import MagicMock, patch

from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent

from src.app import lambda_handler, handle_text_message, line_bot_api


class TestApp:
    """Test cases for the refactored app.py using line-bot-sdk."""

    def setup_method(self):
        """Set up test environment variables before each test."""
        self.patcher = patch.dict(os.environ, {
            'LINE_CHANNEL_SECRET': 'test-secret',
            'LINE_CHANNEL_ACCESS_TOKEN': 'test-token'
        })
        self.patcher.start()

    def teardown_method(self):
        """Clean up environment variables after each test."""
        self.patcher.stop()

    @patch('src.app.handler')
    def test_lambda_handler_success(self, mock_handler):
        """Test lambda_handler successfully processes a valid event."""

        event = {
            'headers': {'x-line-signature': 'valid-signature'},
            'body': '{"events":[]}'
        }

        # Act
        result = lambda_handler(event, None)

        # Assert
        mock_handler.handle.assert_called_once_with('{"events":[]}', 'valid-signature')
        assert result['statusCode'] == 200
        assert json.loads(result['body'])['message'] == 'Webhook processed successfully'

    @patch('src.app.handler')
    def test_lambda_handler_invalid_signature(self, mock_handler):
        """Test lambda_handler returns 400 on InvalidSignatureError."""
        mock_handler.handle.side_effect = InvalidSignatureError("Invalid signature")

        event = {
            'headers': {'x-line-signature': 'invalid-signature'},
            'body': '{"events":[]}'
        }

        # Act
        result = lambda_handler(event, None)

        # Assert
        assert result['statusCode'] == 400
        assert json.loads(result['body'])['error'] == 'Invalid signature'

    @patch('src.app.handler')
    def test_lambda_handler_general_exception(self, mock_handler):
        """Test lambda_handler returns 500 on a general exception."""
        mock_handler.handle.side_effect = Exception("Something went wrong")

        event = {
            'headers': {'x-line-signature': 'valid-signature'},
            'body': '{"events":[]}'
        }

        # Act
        result = lambda_handler(event, None)

        # Assert
        assert result['statusCode'] == 500
        assert json.loads(result['body'])['error'] == 'Internal server error'

    @patch('src.app.send_reply_message')
    @patch('src.app.parse_line_command')
    def test_text_message_event_with_command(self, mock_parse_command, mock_send_reply):
        """Test that a text message with a valid command triggers a reply."""
        # This is an integration-style test of the handler logic
        # Arrange
        mock_parse_command.return_value = "Stock Price: $100"

        # Simulate the SDK calling the decorated handler

        mock_event = MagicMock(spec=MessageEvent)
        mock_event.reply_token = 'test-reply-token'
        mock_event.message = MagicMock(spec=TextMessageContent)
        mock_event.message.text = '#AAPL'
        mock_event.message.mark_as_read_token = None

        # Act
        handle_text_message(mock_event)

        # Assert
        mock_parse_command.assert_called_once_with('#AAPL')
        mock_send_reply.assert_called_once_with(line_bot_api, 'test-reply-token', "Stock Price: $100")

    @patch('src.app.send_reply_message')
    @patch('src.app.parse_line_command')
    def test_text_message_event_no_command(self, mock_parse_command, mock_send_reply):
        """Test that a text message without a command does not trigger a reply."""
        # Arrange
        mock_parse_command.return_value = None

        mock_event = MagicMock(spec=MessageEvent)
        mock_event.reply_token = 'test-reply-token'
        mock_event.message = MagicMock(spec=TextMessageContent)
        mock_event.message.text = 'hello world'
        mock_event.message.mark_as_read_token = None

        # Act
        handle_text_message(mock_event)

        # Assert
        mock_parse_command.assert_called_once_with('hello world')
        mock_send_reply.assert_not_called()
