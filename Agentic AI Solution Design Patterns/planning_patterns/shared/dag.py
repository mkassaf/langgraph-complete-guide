"""
Directed Acyclic Graph for task dependencies.

From lesson: 'converts it into... a Directed Acyclic Graph or DAG,
which explicitly maps the dependencies between the tasks to identify
which are blocked by others and which can be run concurrently'
"""

from dataclasses import dataclass, field


@dataclass
class DAGNode:
    """A task node in the Directed Acyclic Graph."""

    task_id: str
    tool_name: str
    params: dict
    dependencies: list[str]
    can_parallel: bool = False


class DAG:
    """
    Directed Acyclic Graph for task dependencies.
    Each layer = tasks that can run in parallel.
    """

    def __init__(self):
        self.nodes: dict[str, DAGNode] = {}
        self.execution_layers: list[list[str]] = []

    def add_node(self, node: DAGNode):
        """Add task to graph."""
        self.nodes[node.task_id] = node

    def compute_execution_layers(self):
        """
        Topological sort to find parallel groups.
        Layer 0: tasks with no dependencies (run first, in parallel)
        Layer 1: tasks whose deps are in layer 0, etc.
        """
        remaining = set(self.nodes.keys())
        self.execution_layers = []

        while remaining:
            layer = []
            for tid in remaining:
                node = self.nodes[tid]
                deps_satisfied = all(
                    d not in remaining for d in node.dependencies
                )
                if deps_satisfied:
                    layer.append(tid)
            for tid in layer:
                remaining.discard(tid)
            self.execution_layers.append(layer)

    def visualize(self) -> str:
        """ASCII visualization of the DAG."""
        lines = []
        for i, layer in enumerate(self.execution_layers):
            parallel = len(layer) > 1
            label = "PARALLEL" if parallel else "SEQUENTIAL"
            tasks = ", ".join(layer)
            lines.append(f"Layer {i} ({label}): [{tasks}]")
        return "\n".join(lines)
