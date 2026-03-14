"""
Tool Discovery — Controller

Two modes: all_tools (inefficient) vs discovery (efficient).
"""

import ast
import re
from dataclasses import dataclass

from config import MAX_TOOLS_PER_PROMPT
from llm_client import LLMClient, estimate_tokens
from prompts import ALL_TOOLS_PROMPT, DISCOVERY_PROMPT
from registry.tool_registry import ToolRegistry
from registry.tool_spec import ToolSpec


@dataclass
class ToolDiscoveryEvent:
    query: str
    tools_found: list[ToolSpec]
    tool_selected: str
    execution_result: dict


@dataclass
class ControllerResult:
    mode: str
    task: str
    prompt_tokens_used: int
    discovery_events: list[ToolDiscoveryEvent]
    final_answer: str
    tools_actually_used: list[str]


def _parse_action(action_str: str) -> tuple[str, dict]:
    """Parse 'tool_name(params)' or 'discover_tools(need="x")'."""
    action_str = action_str.strip()
    m = re.match(r"(\w+)\s*\((.*)\)\s*$", action_str, re.DOTALL)
    if not m:
        return "", {}
    name, args_str = m.group(1), m.group(2).strip()
    kwargs = {}
    for part in re.split(r",\s*(?![^\[\]]*\])", args_str):
        if "=" not in part:
            continue
        k, v = part.split("=", 1)
        k, v = k.strip(), v.strip()
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
    return name, kwargs


class Controller:
    """
    Two modes:
    Mode 1 (all_tools): Include ALL tool descriptions upfront
    Mode 2 (discovery): Dynamic discovery via registry queries
    """

    def __init__(self, llm_client: LLMClient, registry: ToolRegistry, tools: dict):
        self.llm = llm_client
        self.registry = registry
        self.tools = tools

    def run_all_tools_mode(self, task: str) -> ControllerResult:
        """Load all 24 tool descriptions into prompt."""
        all_descs = "\n".join(
            spec.to_full_spec() for spec in self.registry.tools.values()
        )
        prompt = ALL_TOOLS_PROMPT.format(all_tools_descriptions=all_descs)
        prompt_tokens = estimate_tokens(prompt) + estimate_tokens(task)

        messages = [{"role": "user", "content": task}]
        tools_used = []
        final_answer = ""

        for _ in range(5):
            resp = self.llm.generate(prompt, messages)
            if resp.is_complete and resp.final:
                final_answer = resp.final
                break
            if resp.action:
                name, kwargs = _parse_action(resp.action)
                if name and name != "discover_tools":
                    tool_fn = self.tools.get(f"{name}_tool") or self.tools.get(name)
                    if tool_fn:
                        result = tool_fn(**kwargs)
                        tools_used.append(name)
                        obs = str(result.get("message", result))
                    else:
                        obs = f"Tool {name} not found"
                else:
                    obs = "No valid action"
                messages.append({"role": "assistant", "content": resp.raw_content})
                messages.append({"role": "user", "content": f"OBSERVATION: {obs}\n\nContinue or FINAL: [summary]"})
            else:
                break

        return ControllerResult(
            mode="all_tools",
            task=task,
            prompt_tokens_used=prompt_tokens,
            discovery_events=[],
            final_answer=final_answer or "Task incomplete",
            tools_actually_used=tools_used,
        )

    def run_discovery_mode(self, task: str) -> ControllerResult:
        """Dynamic tool discovery."""
        summary = self.registry.get_registry_summary()
        prompt = DISCOVERY_PROMPT.format(
            tool_count=len(self.registry.tools),
            category_count=len(self.registry.categories),
        )
        initial_tokens = estimate_tokens(prompt) + estimate_tokens(task)
        prompt_tokens = initial_tokens

        messages = [{"role": "user", "content": task}]
        discovery_events = []
        tools_used = []
        discovered_tools: list[ToolSpec] = []
        final_answer = ""

        for _ in range(8):
            resp = self.llm.generate(prompt, messages)
            if resp.is_complete and resp.final:
                final_answer = resp.final
                break
            if not resp.action:
                break

            name, kwargs = _parse_action(resp.action)

            if name == "discover_tools":
                need = kwargs.get("need", task)
                found = self.registry.discover_tools(need, max_results=MAX_TOOLS_PER_PROMPT)
                discovered_tools = found
                obs = self.format_tools_for_llm(found)
                discovery_events.append(ToolDiscoveryEvent(
                    query=need,
                    tools_found=found,
                    tool_selected="",
                    execution_result={},
                ))
                prompt += f"\n\nAVAILABLE TOOLS (from discovery):\n{obs}"
                prompt_tokens = estimate_tokens(prompt)
                messages.append({"role": "assistant", "content": resp.raw_content})
                messages.append({"role": "user", "content": f"OBSERVATION: Found {len(found)} relevant tools:\n{obs}\n\nPick one and use it: ACTION: tool_name(params)"})
            else:
                tool_fn = self.tools.get(f"{name}_tool") or self.tools.get(name)
                if tool_fn:
                    result = tool_fn(**kwargs)
                    tools_used.append(name)
                    obs = str(result.get("message", result))
                    if discovery_events:
                        discovery_events[-1].tool_selected = name
                        discovery_events[-1].execution_result = result
                else:
                    obs = f"Tool {name} not found. Use discover_tools(need='...') first."
                messages.append({"role": "assistant", "content": resp.raw_content})
                messages.append({"role": "user", "content": f"OBSERVATION: {obs}\n\nContinue or FINAL: [summary]"})

        return ControllerResult(
            mode="discovery",
            task=task,
            prompt_tokens_used=prompt_tokens,
            discovery_events=discovery_events,
            final_answer=final_answer or "Task incomplete",
            tools_actually_used=tools_used,
        )

    def format_tools_for_llm(self, tools: list[ToolSpec]) -> str:
        """Format tool specs compactly for LLM context."""
        return "\n".join(f"{i+1}. {t.to_short_description()}" for i, t in enumerate(tools))
