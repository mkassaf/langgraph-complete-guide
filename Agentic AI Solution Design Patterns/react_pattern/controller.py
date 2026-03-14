"""
ReAct Pattern — Controller Module

The intermediary between LLM and external tools.
LLM tells it WHAT to do, Controller knows HOW to do it.
"""

import ast
import re
from dataclasses import dataclass

from llm_client import LLMClient, LLMResponse
from prompts import REACT_SYSTEM_PROMPT
from tools.base_tool import BaseTool, ToolResult


@dataclass
class ReactResult:
    """Result of ReAct loop execution."""
    success: bool
    iterations: int
    action_log: list[dict]
    final_answer: str
    document_created: bool


def _parse_action_string(action_str: str) -> tuple[str, dict]:
    """
    Parse "tool_name(param1=value1, param2=value2)" into (name, kwargs).
    """
    action_str = action_str.strip()
    m = re.match(r"(\w+)\s*\((.*)\)\s*$", action_str, re.DOTALL)
    if not m:
        return "", {}

    tool_name = m.group(1)
    args_str = m.group(2).strip()
    if not args_str:
        return tool_name, {}

    kwargs = {}
    # Split by comma, but not inside brackets
    parts = re.split(r",\s*(?![^\[\]]*\])", args_str)
    for part in parts:
        if "=" not in part:
            continue
        k, v = part.split("=", 1)
        k = k.strip()
        v = v.strip()
        try:
            if v.startswith("[") and v.endswith("]"):
                kwargs[k] = ast.literal_eval(v)
            elif v.startswith('"') or v.startswith("'"):
                kwargs[k] = v.strip('"\'')
            else:
                try:
                    kwargs[k] = int(v)
                except ValueError:
                    kwargs[k] = v
        except (ValueError, SyntaxError):
            kwargs[k] = v.strip('"\'')
    return tool_name, kwargs


class Controller:
    """
    The intermediary between LLM and external tools.

    Core responsibilities:
    1. Maintain conversation history for LLM context
    2. Parse ACTION commands from LLM output
    3. Route actions to correct tools
    4. Feed OBSERVATION results back to LLM
    5. Detect loop completion (FINAL block)

    This is the Controller module from the ReAct design pattern.
    LLM tells it WHAT to do, Controller knows HOW to do it.
    """

    def __init__(self, llm_client: LLMClient, tools: list[BaseTool]):
        self.llm = llm_client
        self.tools = {tool.name: tool for tool in tools}
        self.conversation_history: list[dict] = []
        self.action_log: list[dict] = []

    def run_react_loop(
        self,
        user_request: str,
        max_iterations: int = 10,
    ) -> ReactResult:
        """
        Main ReAct loop:
        1. Send request to LLM
        2. Parse THOUGHT + ACTION from response
        3. Execute action with tool
        4. Get OBSERVATION
        5. Feed observation back to LLM
        6. Repeat until FINAL or max_iterations
        """
        self.conversation_history = [{"role": "user", "content": user_request}]
        self.action_log = []
        consecutive_failures = 0

        for iteration in range(1, max_iterations + 1):
            response = self.llm.generate(
                system_prompt=REACT_SYSTEM_PROMPT,
                conversation_history=self.conversation_history,
            )

            thought = response.thoughts[-1] if response.thoughts else response.raw_content[:200]
            action_str = response.actions[-1] if response.actions else ""

            self.action_log.append({
                "iteration": iteration,
                "thought": thought,
                "action": action_str,
                "observation": "",
            })

            if response.is_complete and response.final_answer:
                self.action_log[-1]["observation"] = "(FINAL - no action)"
                return ReactResult(
                    success=True,
                    iterations=iteration,
                    action_log=self.action_log,
                    final_answer=response.final_answer,
                    document_created=any(
                        "document_tool" in str(a.get("action", ""))
                        for a in self.action_log
                    ),
                )

            if not action_str:
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response.raw_content,
                })
                self.conversation_history.append({
                    "role": "user",
                    "content": "OBSERVATION: No valid ACTION found. Please output ACTION: tool_name(params) to proceed.",
                })
                continue

            result = self.execute_action(action_str)
            observation = self.build_observation_message(result)
            self.action_log[-1]["observation"] = observation

            if not result.success:
                consecutive_failures += 1
                if consecutive_failures >= 3:
                    return ReactResult(
                        success=False,
                        iterations=iteration,
                        action_log=self.action_log,
                        final_answer="Stopped after 3 consecutive tool failures.",
                        document_created=False,
                    )
            else:
                consecutive_failures = 0

            self.conversation_history.append({
                "role": "assistant",
                "content": response.raw_content,
            })
            self.conversation_history.append({
                "role": "user",
                "content": f"OBSERVATION: {observation}\n\nContinue with next THOUGHT and ACTION, or output FINAL: [summary] if done.",
            })

        return ReactResult(
            success=False,
            iterations=max_iterations,
            action_log=self.action_log,
            final_answer="Max iterations reached.",
            document_created=any(
                "document_tool" in str(a.get("action", ""))
                for a in self.action_log
            ),
        )

    def execute_action(self, action_str: str) -> ToolResult:
        """
        Parse action command string and route to correct tool.
        Example: "calendar_tool(team=['Alice'], month='next_month')"
        """
        tool_name, kwargs = _parse_action_string(action_str)

        if not tool_name or tool_name not in self.tools:
            return ToolResult(
                tool_name=tool_name or "unknown",
                success=False,
                data={},
                observation=f"Tool '{tool_name}' not found. Available: {list(self.tools.keys())}",
            )

        try:
            return self.tools[tool_name].execute(**kwargs)
        except Exception as e:
            return ToolResult(
                tool_name=tool_name,
                success=False,
                data={},
                observation=f"Tool error: {e}",
            )

    def build_observation_message(self, tool_result: ToolResult) -> str:
        """Format tool result as OBSERVATION for LLM context."""
        return tool_result.observation
