import json
import logging
import os
from contextvars import ContextVar
from typing import Any

from openai import OpenAI

from line.command_mappings import get_command_catalog, get_fixed_command_examples
from utils.aws_helper import get_ssm_parameter
from utils.web_search import search_stock_by_market, search_tw_stock, search_us_stock, web_search

logger = logging.getLogger(__name__)
client = None

main_model = os.environ.get("OPENAI_MODEL", "gpt-6-luna")
fallback_models: list[str] = ["gpt-5.6-luna"]
_MAX_TOOL_ROUNDS = 3
_LINE_COMMAND_CONFIDENCE_THRESHOLD = 0.8
_LINE_COMMAND_MAX_CANDIDATES = 5
DEFAULT_USER_AGENT = "pharaoh/1.0"
_current_session_id: ContextVar[str | None] = ContextVar("current_session_id", default=None)


def set_current_session_id(session_id: str | None):
    return _current_session_id.set(session_id)


def get_source_session_id(source: Any) -> str | None:
    """Extract group_id, room_id, or user_id as a session identifier from a LINE source."""
    if source is None:
        return None
    if isinstance(source, dict):
        value = (
            source.get("group_id")
            or source.get("groupId")
            or source.get("room_id")
            or source.get("roomId")
            or source.get("user_id")
            or source.get("userId")
        )
        return str(value).strip() if value else None
    for attr in ("group_id", "room_id", "user_id"):
        value = getattr(source, attr, None)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


WEB_SEARCH_TOOLS = [
    {
        "type": "function",
        "name": "web_search",
        "description": "General web search for latest news or facts.",
        "parameters": {"type": "object", "properties": {"query": {"type": "string", "description": "Search query"}}, "required": ["query"]},
    },
    {
        "type": "function",
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
    {
        "type": "function",
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
]


def _run_tool(name: str, arguments: dict) -> str:
    if name == "web_search":
        return web_search(arguments.get("query", ""))
    if name == "search_tw_stock":
        return search_tw_stock(arguments.get("symbol", ""), name=arguments.get("name"))
    if name == "search_us_stock":
        return search_us_stock(arguments.get("symbol", ""), name=arguments.get("name"))
    return f"Unknown tool: {name}"


def _message_to_dict(message) -> dict:
    payload = {"role": message.role, "content": message.content or ""}
    tool_calls = getattr(message, "tool_calls", None) or []
    if tool_calls:
        payload["tool_calls"] = [
            {"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments or "{}"}} for tc in tool_calls
        ]
    return payload


def build_line_command_prompt(text: str) -> str:
    command_rules = "；".join(
        f"{prefix}（{details['name']}，市場：{', '.join(details['markets'])}）" for prefix, details in get_command_catalog().items()
    )
    fixed_examples = "；".join(get_fixed_command_examples())
    return (
        f"將使用者訊息轉換成最多 {_LINE_COMMAND_MAX_CANDIDATES} 個最可能的 Pharaoh LINE command，依可能性排序。"
        "請先自行判斷標的是台股、美股或加密貨幣，再輸出可直接執行的 ticker。"
        "台股必須使用台股代號（例如台積電使用 2330）；美股與加密貨幣必須使用 Yahoo Finance 可查詢的 ticker"
        "（例如 Apple 使用 AAPL、比特幣使用 BTC-USD、以太幣使用 ETH-USD）。不可把中文公司名稱或幣種名稱直接當作美股 ticker。"
        f"可用指令規則：{command_rules}。固定 alias 與 ticker 對照：{fixed_examples}。"
        "固定 alias 必須保留為使用者可輸入的 command；例如台指期必須輸出 #台指期，不要輸出後端 symbol #TXFR1；"
        "台積期必須輸出 #台積期，不要輸出後端 symbol #CDFR1。指令格式中的 ticker 必須是實際可查詢的代號；"
        "F 只適用台股，不要對美股或加密貨幣產生 F 指令。若使用者只說查詢、價格或多少，優先使用 # 報價；"
        "只有明確要求技術分析、走勢圖或 K 線時，才使用 A、P 或 K。每個候選的 text 必須是簡短、容易理解的中文說明，"
        "用於 LINE 按鈕顯示，不要只重複 command。若完全沒有合理候選，candidates 必須為空陣列。只回傳 JSON："
        '{"candidates":[{"command": string, "text": string, "confidence": number}]}.'
        f"\n使用者訊息：{text}"
    )


def parse_line_candidates(content: str) -> list[dict]:
    content = content or "{}"
    if content.strip().startswith("```"):
        content = content.strip().split("\n", 1)[1].rsplit("\n", 1)[0]
    result = json.loads(content)
    candidates = result.get("candidates", [])
    if not candidates and result.get("command") is not None:
        candidates = [{"command": result.get("command"), "confidence": result.get("confidence", 0)}]
    if not isinstance(candidates, list):
        return []
    valid, seen = [], set()
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        command = candidate.get("command")
        if (
            not (
                isinstance(command, str)
                and (command == "D除息" or (1 < len(command) <= 20 and command.startswith(("#", "A", "F", "P", "K", "D", "d"))))
            )
            or command in seen
        ):
            continue
        display = candidate.get("text")
        display = display.strip()[:20] if isinstance(display, str) and display.strip() else command
        try:
            confidence = float(candidate.get("confidence", 0))
        except (TypeError, ValueError):
            continue
        if 0 <= confidence <= 1:
            seen.add(command)
            valid.append({"command": command, "text": display, "confidence": confidence})
    return sorted(valid, key=lambda item: item["confidence"], reverse=True)[:_LINE_COMMAND_MAX_CANDIDATES]


def get_openai_client() -> OpenAI:
    """Return a shared OpenAI client. The key is read from OPENAI_API_KEY, then SSM `openai/api-key`."""
    global client
    if client is None:
        client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY") or get_ssm_parameter("openai/api-key"),
            base_url=os.environ.get("OPENAI_BASE_URL") or None,
            default_headers={"User-Agent": DEFAULT_USER_AGENT},
        )
    return client


def _chat_with_tools(openai_client: Any, model: str, messages: list[dict]) -> str:
    for _ in range(_MAX_TOOL_ROUNDS + 1):
        response = openai_client.responses.create(
            model=model,
            input=messages,
            tools=WEB_SEARCH_TOOLS,
            tool_choice="auto",
            reasoning={"effort": "none"},
        )
        output = getattr(response, "output", []) or []
        tool_calls = [item for item in output if getattr(item, "type", None) == "function_call"]
        if not tool_calls:
            return getattr(response, "output_text", "") or ""

        messages.extend(output)
        for tool_call in tool_calls:
            try:
                args = json.loads(tool_call.arguments or "{}")
            except ValueError:
                args = {}
            result = _run_tool(tool_call.name, args)
            messages.append(
                {
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": result or "(no results)",
                }
            )

    return ""


def infer_line_candidate_commands(text: str, session_id: str | None = None) -> list[dict]:
    """Infer up to five supported LINE commands, ordered by confidence."""
    prompt = build_line_command_prompt(text)
    try:
        openai_client = get_openai_client()
        response = None
        for model in (main_model, *fallback_models):
            try:
                response = openai_client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                )
                break
            except Exception as error:
                logger.warning("LINE command inference failed with %s: %s", model, error)

        if response is None:
            return []

        return parse_line_candidates(response.choices[0].message.content or "{}")
    except Exception as error:
        logger.warning("Unable to infer LINE commands: %s", error)
        return []


def infer_line_command(text: str, session_id: str | None = None) -> str | None:
    """Infer one supported LINE command only when confidence is high enough."""
    candidates = infer_line_candidate_commands(text, session_id=session_id)
    if not candidates or candidates[0]["confidence"] < _LINE_COMMAND_CONFIDENCE_THRESHOLD:
        return None
    return candidates[0]["command"]


def generate_openai_technical_analysis_response(
    prompt_content: str,
    *,
    symbol: str | None = None,
    market_type: str | None = None,
    name: str | None = None,
    session_id: str | None = None,
) -> str:
    contents = (
        "根據以下資料用技術分析與基本面分析這檔股票，技術分析為主，基本面需要提供具體數字，"
        "不要提及資料來源，不要markdown格式，不需要提醒投資者任何警語。"
        "若基本面資料不足，可呼叫 search_tw_stock（台股）或 search_us_stock（美股）或 web_search 取得最新資料後再分析。"
        f"\n {prompt_content}"
    )

    if symbol and market_type:
        latest = search_stock_by_market(symbol, market_type, name=name)
        if latest:
            contents += f"\n\n最新查詢資料:\n{latest}"
    openai_client = get_openai_client()
    messages = [{"role": "user", "content": contents}]
    last_error = None
    for model in (main_model, *fallback_models):
        try:
            return _chat_with_tools(openai_client, model, list(messages))
        except Exception as error:
            logger.exception(error)
            last_error = error
    raise last_error
