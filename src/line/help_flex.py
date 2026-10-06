from linebot.v3.messaging import FlexContainer, FlexMessage, MessageAction


def _create_button(label: str, text: str) -> dict:
    """Build a compact button triggering a message action."""
    return {
        "type": "button",
        "style": "secondary",
        "height": "sm",
        "action": MessageAction(label=label, text=text).to_dict(),
    }


def _create_command_item(title: str, desc: str, example: str | None = None, title_color: str = "#2563EB") -> dict:
    """Build an individual command row with bold prefix, description, and subtle example text."""
    contents = [
        {
            "type": "box",
            "layout": "baseline",
            "spacing": "sm",
            "contents": [
                {"type": "text", "text": title, "weight": "bold", "size": "sm", "color": title_color, "flex": 0},
                {"type": "text", "text": desc, "size": "sm", "color": "#334155", "flex": 1, "wrap": True},
            ],
        }
    ]
    if example:
        contents.append(
            {
                "type": "text",
                "text": example,
                "size": "xxs",
                "color": "#64748B",
                "margin": "xs",
                "wrap": True,
            }
        )
    return {
        "type": "box",
        "layout": "vertical",
        "spacing": "none",
        "contents": contents,
    }


def create_command_help_flex() -> FlexMessage:
    """Build a multi-card carousel Flex Message detailing bot commands and interactive examples."""
    cards = [
        {
            "type": "bubble",
            "size": "mega",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "📊 個股與圖表", "weight": "bold", "size": "lg", "color": "#2563EB"},
                    {"type": "text", "text": "即時報價、走勢圖、K線與股利", "size": "xs", "color": "#64748B", "margin": "xs"},
                ],
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {"type": "separator"},
                    _create_command_item("#代號", "即時報價 (台/美股/ETF)", "例：#2330、#AAPL、#台積電", title_color="#2563EB"),
                    _create_command_item("P代號", "當日分時走勢圖", "例：P2330、PTSLA、P台積電", title_color="#2563EB"),
                    _create_command_item("K代號", "半年 K 線圖 (含均線與量)", "例：K2330、KNVDA", title_color="#2563EB"),
                    _create_command_item("D代號", "歷年股利走勢圖", "例：D2330、D2603", title_color="#2563EB"),
                    _create_command_item("D除息", "今日除權息股票清單", "顯示當日除息股票與現金股利", title_color="#2563EB"),
                ],
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "xs",
                "contents": [
                    {"type": "separator"},
                    {"type": "text", "text": "點擊範例直接查詢", "size": "xxs", "color": "#94A3B8", "align": "center", "margin": "sm"},
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "spacing": "sm",
                        "contents": [_create_button("#2330", "#2330"), _create_button("P2330", "P2330")],
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "spacing": "sm",
                        "contents": [_create_button("K2330", "K2330"), _create_button("D除息", "D除息")],
                    },
                ],
            },
        },
        {
            "type": "bubble",
            "size": "mega",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "🤖 AI 分析與籌碼", "weight": "bold", "size": "lg", "color": "#7C3AED"},
                    {"type": "text", "text": "均線評估、AI 智能點評、法人動態", "size": "xs", "color": "#64748B", "margin": "xs"},
                ],
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {"type": "separator"},
                    _create_command_item("A代號", "AI 技術分析評估", "含 5MA/月/季/半年/年線與 AI 智能盤勢點評", title_color="#7C3AED"),
                    _create_command_item("A大盤", "台股大盤技術分析", "加權指數技術面指標與 AI 觀點", title_color="#7C3AED"),
                    _create_command_item("F代號", "三大法人買賣超 (台股)", "外資、投信、自營商買賣超張數 (例：F2330)", title_color="#7C3AED"),
                    _create_command_item("F大盤", "大盤法人買賣超", "今日整體市場法人動態與買賣超統計", title_color="#7C3AED"),
                ],
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "xs",
                "contents": [
                    {"type": "separator"},
                    {"type": "text", "text": "點擊範例直接查詢", "size": "xxs", "color": "#94A3B8", "align": "center", "margin": "sm"},
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "spacing": "sm",
                        "contents": [_create_button("A2330", "A2330"), _create_button("F2330", "F2330")],
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "spacing": "sm",
                        "contents": [_create_button("A大盤", "A大盤"), _create_button("F大盤", "F大盤")],
                    },
                ],
            },
        },
        {
            "type": "bubble",
            "size": "mega",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "📈 指數與期貨", "weight": "bold", "size": "lg", "color": "#D97706"},
                    {"type": "text", "text": "全球大盤指數與台美期貨即時行情", "size": "xs", "color": "#64748B", "margin": "xs"},
                ],
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {"type": "separator"},
                    _create_command_item("#大盤 / #櫃買", "台灣指數", "加權指數 (#大盤)、櫃買指數 (#櫃買)", title_color="#D97706"),
                    _create_command_item("#美股 / #亞股", "國際指數", "美股四大指數 (#美股)、亞洲主要指數 (#亞股)", title_color="#D97706"),
                    _create_command_item("#台指期", "台灣指數期貨", "台指期貨近月合約即時行情", title_color="#D97706"),
                    _create_command_item("#美股期", "美股指數期貨", "道瓊、標普、那斯達克、費半期貨", title_color="#D97706"),
                    _create_command_item("#台積期", "個股期貨", "台積電股票期貨即時價格", title_color="#D97706"),
                ],
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "xs",
                "contents": [
                    {"type": "separator"},
                    {"type": "text", "text": "點擊範例直接查詢", "size": "xxs", "color": "#94A3B8", "align": "center", "margin": "sm"},
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "spacing": "sm",
                        "contents": [_create_button("#大盤", "#大盤"), _create_button("#美股", "#美股")],
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "spacing": "sm",
                        "contents": [_create_button("#台指期", "#台指期"), _create_button("#台積期", "#台積期")],
                    },
                ],
            },
        },
        {
            "type": "bubble",
            "size": "mega",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "🌐 外匯、商品與幣圈", "weight": "bold", "size": "lg", "color": "#0D9488"},
                    {"type": "text", "text": "匯率、國際原物料、美債、加密貨幣", "size": "xs", "color": "#64748B", "margin": "xs"},
                ],
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {"type": "separator"},
                    _create_command_item("#美元 / #日幣", "外匯匯率", "美元/台幣 (#美元)、日幣/台幣 (#日幣)、#外匯", title_color="#0D9488"),
                    _create_command_item("#黃金 / #原油", "國際原物料", "紐約黃金 (#黃金)、紐約輕原油 (#原油)、#貴金屬", title_color="#0D9488"),
                    _create_command_item("#美債", "美國國債殖利率", "5年期、10年期、30年期國債殖利率", title_color="#0D9488"),
                    _create_command_item("#比特幣 / #以太幣", "加密貨幣", "BTC-USD (#比特幣)、ETH-USD (#以太幣)", title_color="#0D9488"),
                ],
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "xs",
                "contents": [
                    {"type": "separator"},
                    {"type": "text", "text": "點擊範例直接查詢", "size": "xxs", "color": "#94A3B8", "align": "center", "margin": "sm"},
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "spacing": "sm",
                        "contents": [_create_button("#美元", "#美元"), _create_button("#日幣", "#日幣")],
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "spacing": "sm",
                        "contents": [_create_button("#黃金", "#黃金"), _create_button("#比特幣", "#比特幣")],
                    },
                ],
            },
        },
    ]

    return FlexMessage(
        alt_text="Pharaoh 指令說明",
        contents=FlexContainer.from_dict({"type": "carousel", "contents": cards}),
    )
