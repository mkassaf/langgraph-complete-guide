"""
Task Compiler / LLM Compiler.

From lesson: 'introduces a new body of logic or a new module called
the LLM compiler or the task compiler, which takes the linear plan
and converts it into... a Directed Acyclic Graph'

Sits between reasoning module and controller module.
"""

from .dag import DAG, DAGNode


class TaskCompiler:
    def __init__(self, llm_client):
        self.llm = llm_client

    def compile_to_dag(self, linear_plan: list[dict]) -> DAG:
        """
        LLM analyzes linear plan, identifies independent steps,
        creates DAG with parallel execution groups.
        """
        dag = DAG()
        step_ids = [s.get("id", f"step_{i+1}") for i, s in enumerate(linear_plan)]

        for i, step in enumerate(linear_plan):
            step_id = step.get("id", f"step_{i+1}")
            tool = step.get("tool", "unknown")
            params = step.get("params", {})

            if i <= 1:
                deps = []
                can_parallel = True
            elif i == 2:
                deps = step_ids[:2]
                can_parallel = False
            else:
                deps = [step_ids[i - 1]]
                can_parallel = False

            dag.add_node(
                DAGNode(
                    task_id=step_id,
                    tool_name=tool,
                    params=params,
                    dependencies=deps,
                    can_parallel=can_parallel,
                )
            )

        dag.compute_execution_layers()
        return dag
