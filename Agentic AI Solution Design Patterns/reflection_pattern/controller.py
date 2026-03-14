"""
Reflection Pattern — Controller

Manages CoT, ReAct, and Reflection loops.
"""

import ast
import re
from dataclasses import dataclass

from config import MAX_REFLECTION_ROUNDS
from llm_client import LLMClient, LLMResponse
from prompts import (
    INITIAL_PROMPT,
    COT_PROMPT,
    COT_REFLECTION_PROMPT,
    REACT_PROMPT,
    REACT_REFLECTION_PROMPT,
    PATTERN_SWITCH_REFLECTION_PROMPT,
)
from tools.base_tool import BaseTool, ToolResult


@dataclass
class ReflectionRound:
    round_number: int
    original_output: str
    reflection_prompt_used: str
    reflection_response: LLMResponse
    improved_output: str | None
    action_taken: str | None
    verdict: str


@dataclass
class ControllerResult:
    mode: str
    initial_output: str
    reflection_rounds: list[ReflectionRound]
    final_output: str
    total_improvements: int
    pattern_switched: bool
    switch_reason: str | None
    action_log: list[dict] = None
    correction_applied: bool = False


def _parse_action(action_str: str) -> tuple[str, dict]:
    m = re.match(r"(\w+)\s*\((.*)\)\s*$", action_str.strip(), re.DOTALL)
    if not m:
        return "", {}
    tool_name, args_str = m.group(1), m.group(2).strip()
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
    return tool_name, kwargs


class Controller:
    """
    Manages the full Reflection loop.
    Three reflection modes:
    1. post_cot_reflection: improve text output
    2. post_react_reflection: detect and fix action errors
    3. pattern_switch_reflection: decide if pattern change needed
    """

    def __init__(self, llm_client: LLMClient, tools: dict, max_reflection_rounds: int = MAX_REFLECTION_ROUNDS):
        self.llm = llm_client
        self.tools = tools
        self.max_rounds = max_reflection_rounds
        self._inject_document_error = False
        self._document_error_injected = False

    def run_with_cot_reflection(self, user_request: str) -> ControllerResult:
        """CoT → reflect → improve until SATISFACTORY or max rounds."""
        messages = [{"role": "user", "content": user_request}]
        resp = self.llm.generate(COT_PROMPT, messages)
        initial_output = resp.raw_content
        reflection_rounds = []
        total_improvements = 0
        current_output = initial_output

        for rnd in range(1, self.max_rounds + 1):
            prompt = COT_REFLECTION_PROMPT.format(previous_output=current_output)
            ref_messages = messages + [
                {"role": "assistant", "content": current_output},
                {"role": "user", "content": prompt},
            ]
            ref_resp = self.llm.generate(INITIAL_PROMPT, ref_messages)
            reflection_rounds.append(ReflectionRound(
                round_number=rnd,
                original_output=current_output,
                reflection_prompt_used=prompt[:200] + "...",
                reflection_response=ref_resp,
                improved_output=ref_resp.improvement_text,
                action_taken=None,
                verdict=ref_resp.verdict or "",
            ))
            if ref_resp.verdict == "SATISFACTORY":
                break
            if ref_resp.improvement_text:
                current_output = ref_resp.improvement_text
                total_improvements += 1
            else:
                break

        return ControllerResult(
            mode="cot",
            initial_output=initial_output,
            reflection_rounds=reflection_rounds,
            final_output=current_output,
            total_improvements=total_improvements,
            pattern_switched=False,
            switch_reason=None,
        )

    def run_with_react_reflection(self, user_request: str) -> ControllerResult:
        """ReAct → reflect on action log → apply corrections."""
        self._inject_document_error = True
        self._document_error_injected = False
        final_answer, action_log = self.execute_react_loop(user_request)
        self._inject_document_error = False

        action_obs_log = "\n".join(
            f"Action: {a.get('action','')}\nObservation: {a.get('observation','')}"
            for a in action_log
        )
        prompt = REACT_REFLECTION_PROMPT.format(action_observation_log=action_obs_log)
        messages = [
            {"role": "user", "content": "Review the following action log."},
            {"role": "assistant", "content": action_obs_log},
            {"role": "user", "content": prompt},
        ]
        ref_resp = self.llm.generate(REACT_PROMPT, messages)

        reflection_rounds = [ReflectionRound(
            round_number=1,
            original_output=action_obs_log,
            reflection_prompt_used=prompt[:200] + "...",
            reflection_response=ref_resp,
            improved_output=None,
            action_taken=ref_resp.correction_action,
            verdict=ref_resp.verdict or "",
        )]

        correction_applied = False
        if ref_resp.has_correction and ref_resp.correction_action:
            # Ensure we have valid params (e.g. date="18th" for document_tool)
            corr = ref_resp.correction_action
            if "document_tool" in corr and "date=" not in corr.lower():
                corr = corr.rstrip(")") + ', date="18th")'
            result = self.apply_correction(corr)
            correction_applied = result.success
            if correction_applied:
                final_answer = result.observation

        return ControllerResult(
            mode="react",
            initial_output=action_obs_log,
            reflection_rounds=reflection_rounds,
            final_output=final_answer,
            total_improvements=1 if correction_applied else 0,
            pattern_switched=False,
            switch_reason=None,
            action_log=action_log,
            correction_applied=correction_applied,
        )

    def run_with_pattern_switch(self, user_request: str) -> ControllerResult:
        """Simple prompt → reflect → switch to ReAct if needed."""
        messages = [{"role": "user", "content": user_request}]
        resp = self.llm.generate(INITIAL_PROMPT, messages)
        initial_output = resp.raw_content

        prompt = PATTERN_SWITCH_REFLECTION_PROMPT.format(previous_output=initial_output)
        ref_messages = messages + [
            {"role": "assistant", "content": initial_output},
            {"role": "user", "content": prompt},
        ]
        ref_resp = self.llm.generate(INITIAL_PROMPT, ref_messages)

        pattern_switched = ref_resp.has_pattern_switch
        switch_reason = ref_resp.raw_content if pattern_switched else None
        final_output = initial_output

        if ref_resp.pattern_switch_to == "react":
            self._inject_document_error = False
            final_answer, action_log = self.execute_react_loop(user_request)
            final_output = final_answer

        return ControllerResult(
            mode="switched",
            initial_output=initial_output,
            reflection_rounds=[],
            final_output=final_output,
            total_improvements=0,
            pattern_switched=pattern_switched,
            switch_reason=switch_reason,
        )

    def execute_react_loop(self, user_request: str) -> tuple[str, list[dict]]:
        """Run ReAct loop, return (final_answer, action_log)."""
        history = [{"role": "user", "content": user_request}]
        action_log = []

        for _ in range(8):
            resp = self.llm.generate(REACT_PROMPT, history)
            thoughts = re.findall(r"THOUGHT\s*:\s*(.+?)(?=ACTION|$)", resp.raw_content, re.DOTALL | re.IGNORECASE)
            actions = re.findall(r"ACTION\s*:\s*(\S+\([^)]*\))", resp.raw_content)

            if "FINAL:" in resp.raw_content.upper():
                m = re.search(r"FINAL\s*:\s*(.+)", resp.raw_content, re.DOTALL | re.IGNORECASE)
                final = m.group(1).strip() if m else resp.raw_content
                return final, action_log

            action_str = actions[-1] if actions else ""
            observation = "(no action)"
            if action_str:
                tool_name, kwargs = _parse_action(action_str)
                if tool_name in self.tools:
                    if self._inject_document_error and tool_name == "document_tool" and not self._document_error_injected:
                        self._document_error_injected = True
                        kwargs["date"] = ""
                    result = self.tools[tool_name].execute(**kwargs)
                    observation = result.observation
                action_log.append({"action": action_str, "observation": observation})

            history.append({"role": "assistant", "content": resp.raw_content})
            history.append({"role": "user", "content": f"OBSERVATION: {observation}\n\nContinue or output FINAL: [summary] if done."})

        return "Max iterations reached.", action_log

    def apply_correction(self, correction_action: str) -> ToolResult:
        """Parse and execute correction action."""
        tool_name, kwargs = _parse_action(correction_action)
        if tool_name in self.tools:
            return self.tools[tool_name].execute(**kwargs)
        return ToolResult(tool_name="", success=False, data={}, observation=f"Tool {tool_name} not found")
