from routing.data_quality import conflicting_results, missing_critical_data
from routing.models import Freshness
from routing.tool_results import ToolResult


def source_note(results: list[ToolResult], freshness: Freshness) -> str:
    if freshness == Freshness.STATIC:
        return ""
    notes = []
    for result in results:
        timestamp = result.effective_at or result.retrieved_at
        notes.append(f"來源：{result.source}（資料時間：{timestamp}）")
    if conflicting_results(results):
        notes.append("注意：不同來源的資料不一致，請以原始來源進一步核對。")
    return "\n".join(notes)


def answer_data_status(results: list[ToolResult], freshness: Freshness) -> str:
    if missing_critical_data(results):
        return "目前缺少足夠的可靠資料，無法做出可靠判斷。"
    return source_note(results, freshness)
