"""
Chain of Thought — Agent with Controller + LLM

Implements the Controller module from the design pattern:
Controller acts as intermediary between LLM and outside world.
"""

import re
from dataclasses import dataclass

from config import MAX_TOKENS, MODEL
from llm_client import LLMClient, LLMResponse
from prompts import COT_SYSTEM_PROMPT, NO_COT_SYSTEM_PROMPT


@dataclass
class ControllerResult:
    """Result from processing a user request."""
    mode: str  # "standard" | "chain_of_thought"
    llm_response: LLMResponse
    issues_detected: list[str]
    assumptions_made: list[str]


def _extract_assumptions(text: str) -> list[str]:
    """Find phrases indicating assumptions."""
    assumptions = []
    patterns = [
        r"(?:assuming|assume)[^.]*\.",
        r"I(?:'ll| will) interpret[^.]*\.",
        r"(?:likely|probably|perhaps)[^.]*\.",
        r"(?:I'll suppose|we can assume)[^.]*\.",
        r"without (?:knowing|checking)[^.]*\.",
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        assumptions.extend(matches)
    return [a.strip() for a in assumptions]


def _extract_issues(text: str) -> list[str]:
    """Detect potential issues in reasoning."""
    issues = []
    if "budget" not in text.lower() and "cost" not in text.lower():
        issues.append("Budget/cost not considered")
    if "availability" not in text.lower() and "schedule" not in text.lower():
        issues.append("Team availability not addressed")
    if "engaging" in text.lower() and "?" not in text and "define" not in text.lower():
        issues.append("'Engaging' not clarified (vague interpretation)")
    return issues


class Controller:
    """
    Acts as intermediary between LLM and outside world.
    Issues system prompts to LLM based on task complexity.
    Implements the Controller module from the design pattern.
    """

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.use_chain_of_thought = False

    def set_chain_of_thought(self, enabled: bool) -> None:
        """Enable or disable CoT system prompt."""
        self.use_chain_of_thought = enabled

    def get_system_prompt(self) -> str:
        """Return appropriate system prompt based on CoT setting."""
        return COT_SYSTEM_PROMPT if self.use_chain_of_thought else NO_COT_SYSTEM_PROMPT

    def process_request(self, user_request: str) -> ControllerResult:
        """
        1. Select system prompt (CoT or not)
        2. Send to LLM
        3. Parse and return result
        """
        system_prompt = self.get_system_prompt()
        mode = "chain_of_thought" if self.use_chain_of_thought else "standard"

        llm_response = self.llm.generate(
            system_prompt=system_prompt,
            user_message=user_request,
            expect_cot=self.use_chain_of_thought,
        )

        issues_detected = _extract_issues(llm_response.content)
        assumptions_made = _extract_assumptions(llm_response.content)

        return ControllerResult(
            mode=mode,
            llm_response=llm_response,
            issues_detected=issues_detected,
            assumptions_made=assumptions_made,
        )


class EventPlanningAgent:
    """
    Full agent for planning team offsite events.
    Contains Controller + LLM as per design pattern.
    """

    def __init__(self):
        self.llm_client = LLMClient(model=MODEL, max_tokens=MAX_TOKENS)
        self.controller = Controller(self.llm_client)

    def plan_without_cot(self, request: str) -> ControllerResult:
        """Run planning with standard prompt - no structured thinking."""
        self.controller.set_chain_of_thought(False)
        return self.controller.process_request(request)

    def plan_with_cot(self, request: str) -> ControllerResult:
        """Run planning with Chain of Thought system prompt."""
        self.controller.set_chain_of_thought(True)
        return self.controller.process_request(request)
