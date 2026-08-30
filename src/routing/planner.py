from routing.models import ExecutionGraph, ExecutionNode, ExecutionPlan


def build_execution_graph(plan: ExecutionPlan) -> ExecutionGraph:
    """Build a dependency graph for the tools and final synthesis step."""
    nodes: list[ExecutionNode] = []
    tool_node_ids: list[str] = []
    for index, tool in enumerate(plan.tools):
        node_id = f"tool-{index + 1}"
        tool_node_ids.append(node_id)
        nodes.append(ExecutionNode(node_id=node_id, kind="tool", operation=tool))

    nodes.append(
        ExecutionNode(
            node_id="answer",
            kind="answer",
            operation="generate_answer",
            depends_on=tool_node_ids,
            inputs=tool_node_ids,
        )
    )
    return ExecutionGraph(nodes=nodes)
