from routing.tool_results import ToolResult


def choose_best_result(results: list[ToolResult]) -> ToolResult | None:
    """Choose the first complete, non-stale result, then the best partial result."""
    usable = [result for result in results if result.data is not None and not result.is_stale and not result.error]
    if usable:
        return usable[0]
    partial = [result for result in results if result.data is not None and not result.is_stale]
    return partial[0] if partial else None


def conflicting_results(results: list[ToolResult]) -> bool:
    values = [result.data for result in results if result.data is not None and not result.error]
    return len({repr(value) for value in values}) > 1


def missing_critical_data(results: list[ToolResult]) -> bool:
    return not results or all(result.data is None or result.is_stale or result.error for result in results)
