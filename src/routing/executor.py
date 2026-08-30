import json

from routing.answer import answer_data_status
from routing.models import Capability, ExecutionPlan
from routing.tools import TOOL_REGISTRY


class FinancialExecutor:
    def execute(self, plan: ExecutionPlan, *, query: str) -> str:
        if plan.capabilities == [Capability.CLARIFICATION]:
            return "請提供更明確的金融標的、問題類型或市場。"
        if plan.capabilities == [Capability.KNOWLEDGE]:
            result = TOOL_REGISTRY["knowledge"](query)
            return result.data or "目前尚未設定知識庫，無法回答此問題。"
        if not plan.entities:
            return "請提供明確的金融標的。"

        results = []
        for tool in plan.tools:
            adapter = TOOL_REGISTRY.get(tool)
            if adapter is None:
                continue
            results.append(adapter(plan.entities[0]))
        status = answer_data_status(results, plan.freshness)
        if not results or not status:
            return "目前沒有可用的資料。"
        data = next((result.data for result in results if result.data is not None and not result.error), None)
        if data is None:
            return status
        rendered = data if isinstance(data, str) else json.dumps(data, ensure_ascii=False, default=str)
        return f"{rendered}\n\n{status}" if status else rendered
