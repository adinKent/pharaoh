from linebot.v3.messaging import FlexCarousel, FlexMessage

from line.help_flex import create_command_help_flex


def test_create_command_help_flex_structure():
    """Verify create_command_help_flex builds a valid carousel FlexMessage with expected cards and buttons."""
    message = create_command_help_flex()

    assert isinstance(message, FlexMessage)
    assert message.alt_text == "Pharaoh 指令說明"
    assert isinstance(message.contents, FlexCarousel)

    bubbles = message.contents.contents
    assert len(bubbles) == 4

    payload = message.contents.to_dict()
    assert payload["type"] == "carousel"
    assert len(payload["contents"]) == 4

    expected_titles = [
        "📊 個股與圖表",
        "🤖 AI 分析與籌碼",
        "📈 指數與期貨",
        "🌐 外匯、商品與幣圈",
    ]

    for bubble, expected_title in zip(payload["contents"], expected_titles, strict=True):
        header_text = bubble["header"]["contents"][0]["text"]
        assert header_text == expected_title

        # Check footer buttons
        footer_contents = bubble["footer"]["contents"]
        button_rows = [item for item in footer_contents if item["type"] == "box" and item.get("layout") == "horizontal"]
        assert len(button_rows) == 2

        actions = []
        for row in button_rows:
            for btn in row["contents"]:
                assert btn["type"] == "button"
                actions.append(btn["action"])

        assert len(actions) == 4
        for action in actions:
            assert action["type"] == "message"
            assert action["label"]
            assert action["text"]


def test_create_command_help_flex_actions():
    """Verify specific key command shortcuts are clickable in the footer."""
    message = create_command_help_flex()
    payload = message.contents.to_dict()

    all_actions = []
    for bubble in payload["contents"]:
        for item in bubble["footer"]["contents"]:
            if item["type"] == "box" and item.get("layout") == "horizontal":
                for btn in item["contents"]:
                    all_actions.append(btn["action"]["text"])

    expected_commands = {
        "#2330",
        "P2330",
        "K2330",
        "D除息",
        "A2330",
        "F2330",
        "A大盤",
        "F大盤",
        "#大盤",
        "#美股",
        "#台指期",
        "#台積期",
        "#美元",
        "#日幣",
        "#黃金",
        "#比特幣",
    }
    assert expected_commands.issubset(set(all_actions))
