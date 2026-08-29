import json
import logging

from openai import OpenAI

from utils.aws_helper import get_ssm_parameter
from utils.web_search import search_stock_by_market, search_tw_stock, search_us_stock, web_search

logger = logging.getLogger(__name__)
client = None

base_url = "https://opencode.ai/zen/go/v1"
main_model = "gpt-5.6-luna"
fallback_models = ["deepseek-v4-flash", "ox-alpha-free"]
_MAX_TOOL_ROUNDS = 3
_LINE_COMMAND_CONFIDENCE_THRESHOLD = 0.8
_LINE_COMMAND_MAX_CANDIDATES = 5

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


def _is_valid_line_command(command: object) -> bool:
    return isinstance(command, str) and (command == "D除息" or (1 < len(command) <= 20 and command.startswith(("#", "A", "F", "P", "K"))))


def infer_line_candidate_commands(text: str) -> list[dict]:
    """Infer up to three supported LINE commands, ordered by confidence."""
    prompt = (
        "將使用者訊息轉換成最多 3 個最可能的 Pharaoh LINE command，依可能性排序。"
        "請先自行判斷標的是台股、美股或加密貨幣，再輸出可直接執行的 ticker。"
        "台股必須使用台股代號（例如台積電使用 2330）；"
        "美股與加密貨幣必須使用 Yahoo Finance 可查詢的 ticker"
        "（例如 Apple 使用 AAPL、比特幣使用 BTC-USD、以太幣使用 ETH-USD）。"
        "不可把中文公司名稱或幣種名稱直接當作美股 ticker。"
        "只能選擇以下格式："
        "#<ticker>（報價）、A<ticker>（技術分析）、F<台股代號>（法人買賣超）、"
        "P<ticker>（當日走勢圖）、K<ticker>（半年K線圖）、D除息。"
        "F 只適用台股，不要對美股或加密貨幣產生 F 指令。"
        "若使用者只說查詢、價格或多少，優先使用 # 報價；"
        "只有明確要求技術分析、走勢圖或 K 線時，才使用 A、P 或 K。"
        "若完全沒有合理候選，candidates 必須為空陣列。只回傳 JSON："
        '{"candidates":[{"command": string, "confidence": number}]}。'
        f"\n使用者訊息：{text}"
    )

    try:
        opencode_client = get_opencode_client()
        response = None
        for model in (main_model, *fallback_models):
            try:
                response = opencode_client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                )
                break
            except Exception as error:
                logger.warning("LINE command inference failed with %s: %s", model, error)

        if response is None:
            return []

        content = response.choices[0].message.content or "{}"
        print(content)

        if content.strip().startswith("```"):
            content = content.strip().split("\n", 1)[1].rsplit("\n", 1)[0]
        result = json.loads(content)
        candidates = result.get("candidates", [])
        # Accept the old response shape while models roll over to the new one.
        if not candidates and result.get("command") is not None:
            candidates = [
                {
                    "command": result.get("command"),
                    "confidence": result.get("confidence", 0),
                }
            ]
        if not isinstance(candidates, list):
            return []

        valid_candidates = []
        seen_commands = set()
        for candidate in candidates:
            if not isinstance(candidate, dict):
                continue
            command = candidate.get("command")
            if not _is_valid_line_command(command) or command in seen_commands:
                continue
            try:
                confidence = float(candidate.get("confidence", 0))
            except (TypeError, ValueError):
                continue
            if not 0 <= confidence <= 1:
                continue
            seen_commands.add(command)
            valid_candidates.append({"command": command, "confidence": confidence})

        return sorted(
            valid_candidates,
            key=lambda candidate: candidate["confidence"],
            reverse=True,
        )[:_LINE_COMMAND_MAX_CANDIDATES]
    except Exception as error:
        logger.warning("Unable to infer LINE commands: %s", error)
        return []


def infer_line_command(text: str) -> str | None:
    """Infer one supported LINE command only when confidence is high enough."""
    candidates = infer_line_candidate_commands(text)
    if not candidates or candidates[0]["confidence"] < _LINE_COMMAND_CONFIDENCE_THRESHOLD:
        return None
    return candidates[0]["command"]


def generate_opencode_technical_analysis_response(
    prompt_content: str,
    *,
    symbol: str | None = None,
    market_type: str | None = None,
    name: str | None = None,
) -> str:
    contents = (
        "根據以下資料用技術分析與基本面分析這檔股票，技術分析為主，基本面需要提供具體數字，"
        "不要提及資料來源，不要markdown格式，內容要在600字內，不需要提醒投資者任何警語。"
        "若基本面資料不足，可呼叫 search_tw_stock（台股）或 search_us_stock（美股）或 web_search 取得最新資料後再分析。"
        f"\n {prompt_content}"
    )

    if symbol and market_type:
        latest = search_stock_by_market(symbol, market_type, name=name)
        if latest:
            contents += f"\n\n最新查詢資料:\n{latest}"

    opencode_client = get_opencode_client()
    messages = [{"role": "user", "content": contents}]

    last_error = None
    for model in (main_model, *fallback_models):
        try:
            return _chat_with_tools(opencode_client, model, list(messages))
        except Exception as error:
            logger.exception(error)
            last_error = error

    raise last_error
