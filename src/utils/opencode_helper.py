import json
import logging

from openai import OpenAI

from utils.aws_helper import get_ssm_parameter
from utils.web_search import search_stock_by_market, search_tw_stock, search_us_stock, web_search

logger = logging.getLogger(__name__)
client = None

base_url = "https://opencode.ai/zen/go/v1"
main_model = "kimi-k2.7-code"
fallback_model = "deepseek-v4-flash"
_MAX_TOOL_ROUNDS = 3

WEB_SEARCH_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "General web search for latest news or facts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_tw_stock",
            "description": "Search latest Taiwan stock fundamentals (profile, dividend, news).",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "TW stock symbol, e.g. 2330"},
                    "name": {"type": "string", "description": "Optional company name"},
                },
                "required": ["symbol"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_us_stock",
            "description": "Search latest US stock fundamentals (stats, profile, analysis, news).",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "US ticker, e.g. AAPL"},
                    "name": {"type": "string", "description": "Optional company name"},
                },
                "required": ["symbol"],
            },
        },
    },
]


def get_opencode_client():
    global client
    if client is None:
        client = OpenAI(
            api_key=get_ssm_parameter("opencode/api-key"),
            base_url=base_url,
        )
    return client


def _run_tool(name: str, arguments: dict) -> str:
    if name == "web_search":
        return web_search(arguments.get("query", ""))
    if name == "search_tw_stock":
        return search_tw_stock(arguments.get("symbol", ""), name=arguments.get("name"))
    if name == "search_us_stock":
        return search_us_stock(arguments.get("symbol", ""), name=arguments.get("name"))
    return f"Unknown tool: {name}"


def _message_to_dict(message) -> dict:
    payload: dict = {
        "role": message.role,
        "content": message.content or "",
    }
    tool_calls = getattr(message, "tool_calls", None) or []
    if tool_calls:
        payload["tool_calls"] = [
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments or "{}",
                },
            }
            for tc in tool_calls
        ]
    return payload


def _chat_with_tools(opencode_client, model: str, messages: list[dict]) -> str:
    for _ in range(_MAX_TOOL_ROUNDS + 1):
        response = opencode_client.chat.completions.create(
            model=model,
            messages=messages,
            tools=WEB_SEARCH_TOOLS,
            tool_choice="auto",
        )
        choice = response.choices[0]
        message = choice.message
        tool_calls = getattr(message, "tool_calls", None) or []
        if not tool_calls:
            return message.content or ""

        messages.append(_message_to_dict(message))
        for tool_call in tool_calls:
            try:
                args = json.loads(tool_call.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            result = _run_tool(tool_call.function.name, args)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result or "(no results)",
                }
            )

    return messages[-1].get("content") if messages[-1].get("role") == "assistant" else ""


def generate_opencode_technical_analysis_response(
    prompt_content: str,
    *,
    symbol: str | None = None,
    market_type: str | None = None,
    name: str | None = None,
) -> str:
    contents = (
        "根據以下資料用技術分析與基本面分析這檔股票，技術分析為主，基本面需要提供具體數字，"
        "不要提及資料來源，不要markdown格式，內容要在500字內，不需要提醒投資者任何警語。"
        "若基本面資料不足，可呼叫 search_tw_stock（台股）或 search_us_stock（美股）或 web_search 取得最新資料後再分析。"
        f"\n {prompt_content}"
    )

    print(f"symbol={symbol}")
    print(f"market_type={market_type}")
    if symbol and market_type:
        latest = search_stock_by_market(symbol, market_type, name=name)
        if latest:
            contents += f"\n\n最新查詢資料:\n{latest}"

    opencode_client = get_opencode_client()
    messages = [{"role": "user", "content": contents}]

    try:
        return _chat_with_tools(opencode_client, main_model, list(messages))
    except Exception as error:
        logger.exception(error)
        return _chat_with_tools(opencode_client, fallback_model, list(messages))
