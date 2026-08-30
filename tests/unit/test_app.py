import json
import os
from unittest.mock import MagicMock, patch

from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent

from app import create_candidate_commands_flex, handle_text_message, lambda_handler, line_bot_api


class TestApp:
    """Test cases for the refactored app.py using line-bot-sdk."""

    def setup_method(self):
        """Set up test environment variables before each test."""
        self.patcher = patch.dict(
            os.environ,
            {
                "LINE_CHANNEL_SECRET": "test-secret",
                "LINE_CHANNEL_ACCESS_TOKEN": "test-token",
            },
        )
        self.patcher.start()

    def teardown_method(self):
        """Clean up environment variables after each test."""
        self.patcher.stop()

    def test_create_candidate_commands_flex_uses_message_actions(self):
        message = create_candidate_commands_flex(
            [
                {"command": "#BTC-USD", "text": "比特幣報價", "confidence": 0.4},
                {"command": "#ETH-USD", "text": "以太幣報價", "confidence": 0.3},
            ]
        )

        payload = message.contents.to_dict()
        assert payload["type"] == "bubble"
        actions = [button["action"] for button in payload["footer"]["contents"]]
        assert actions == [
            {"type": "message", "label": "比特幣報價", "text": "#BTC-USD"},
            {"type": "message", "label": "以太幣報價", "text": "#ETH-USD"},
        ]

    @patch("app.send_reply_flex")
    @patch("app.parse_line_command")
    def test_text_message_event_with_candidate_commands(self, mock_parse_command, mock_send_flex):
        mock_parse_command.return_value = {
            "type": "line_command_candidates",
            "candidates": [{"command": "#BTC-USD", "text": "比特幣報價", "confidence": 0.4}],
        }
        mock_event = MagicMock(spec=MessageEvent)
        mock_event.reply_token = "test-reply-token"
        mock_event.message = MagicMock(spec=TextMessageContent)
        mock_event.message.text = "查詢比特幣"
        mock_event.message.mark_as_read_token = None
        mock_event.source = MagicMock()
        mock_event.source.type = "user"

        handle_text_message(mock_event)

        mock_send_flex.assert_called_once()
        assert isinstance(mock_send_flex.call_args.args[2], type(create_candidate_commands_flex([])))

    @patch("app.handler")
    def test_lambda_handler_success(self, mock_handler):
        """Test lambda_handler successfully processes a valid event."""

        event = {
            "headers": {"x-line-signature": "valid-signature"},
            "body": '{"events":[]}',
        }

        # Act
        result = lambda_handler(event, None)

        # Assert
        mock_handler.handle.assert_called_once_with('{"events":[]}', "valid-signature")
        assert result["statusCode"] == 200
        assert json.loads(result["body"])["message"] == "Webhook processed successfully"

    @patch("app.handler")
    def test_lambda_handler_invalid_signature(self, mock_handler):
        """Test lambda_handler returns 400 on InvalidSignatureError."""
        mock_handler.handle.side_effect = InvalidSignatureError("Invalid signature")

        event = {
            "headers": {"x-line-signature": "invalid-signature"},
            "body": '{"events":[]}',
        }

        # Act
        result = lambda_handler(event, None)

        # Assert
        assert result["statusCode"] == 400
        assert json.loads(result["body"])["error"] == "Invalid signature"

    @patch("app.handler")
    def test_lambda_handler_general_exception(self, mock_handler):
        """Test lambda_handler returns 500 on a general exception."""
        mock_handler.handle.side_effect = Exception("Something went wrong")

        event = {
            "headers": {"x-line-signature": "valid-signature"},
            "body": '{"events":[]}',
        }

        # Act
        result = lambda_handler(event, None)

        # Assert
        assert result["statusCode"] == 500
        assert json.loads(result["body"])["error"] == "Internal server error"

    @patch("app.send_reply_message")
    @patch("app.parse_line_command")
    def test_text_message_event_with_command(self, mock_parse_command, mock_send_reply):
        """Test that a text message with a valid command triggers a reply."""
        # This is an integration-style test of the handler logic
        # Arrange
        mock_parse_command.return_value = "Stock Price: $100"

        # Simulate the SDK calling the decorated handler

        mock_event = MagicMock(spec=MessageEvent)
        mock_event.reply_token = "test-reply-token"
        mock_event.message = MagicMock(spec=TextMessageContent)
        mock_event.message.text = "#AAPL"
        mock_event.message.mark_as_read_token = None
        mock_event.source = MagicMock()
        mock_event.source.type = "user"

        # Act
        handle_text_message(mock_event)

        # Assert
        mock_parse_command.assert_called_once_with("#AAPL", True)
        mock_send_reply.assert_called_once_with(line_bot_api, "test-reply-token", "Stock Price: $100")

    @patch("app.send_reply_message")
    @patch("app.parse_line_command")
    def test_text_message_event_no_command(self, mock_parse_command, mock_send_reply):
        """Test that a text message without a command does not trigger a reply."""
        # Arrange
        mock_parse_command.return_value = None

        mock_event = MagicMock(spec=MessageEvent)
        mock_event.reply_token = "test-reply-token"
        mock_event.message = MagicMock(spec=TextMessageContent)
        mock_event.message.text = "hello world"
        mock_event.message.mark_as_read_token = None
        mock_event.source = MagicMock()
        mock_event.source.type = "group"

        # Act
        handle_text_message(mock_event)

        # Assert
        mock_parse_command.assert_called_once_with("hello world", False)
        mock_send_reply.assert_not_called()

    @patch("app.parse_line_command")
    def test_text_message_mention_of_configured_user_is_one_to_one(self, mock_parse_command):
        """A configured user mention is treated as a one-to-one conversation."""
        mock_event = MagicMock(spec=MessageEvent)
        mock_event.reply_token = "test-reply-token"
        mock_event.message = MagicMock(spec=TextMessageContent)
        mock_event.message.text = "@Bot #AAPL"
        mock_event.message.mark_as_read_token = None
        mock_event.message.mention = MagicMock()
        mock_event.message.mention.mentionees = [MagicMock(is_self=True)]
        mock_event.source = MagicMock()
        mock_event.source.type = "group"

        handle_text_message(mock_event)

        mock_parse_command.assert_called_once_with("@Bot #AAPL", True)
