"""
Reflection Agent — Validates and critiques criterion evaluation results.
For each criterion's output, the reflection agent checks if the decision was applied correctly
and may suggest revision. Used in a reflection loop with each criterion agent.
"""

import re
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.language_models import BaseChatModel


def build_reflection_prompt(criterion_id: str, criterion_description: str, 
                            paper_snippet: str, original_decision: str, original_reason: str) -> str:
    return f"""You are a quality-assurance reviewer for a systematic review screening process.

Criterion [{criterion_id}]: {criterion_description}

Paper (excerpt): {paper_snippet[:800]}...

The screener evaluated this paper and produced:
- Decision: {original_decision}
- Reason: {original_reason}

Review the screener's decision. Check:
1. Was the criterion applied correctly?
2. Is the Decision (Y/N) consistent with the stated Reason?
3. Did the screener miss any relevant information in the paper?

If the decision is correct, respond: APPROVED
If there is an error, respond: REVISE
Then provide a brief explanation (under 50 words) and what the correct decision should be."""


def reflect(model: BaseChatModel, criterion_id: str, criterion_description: str,
            paper_text: str, decision: str, reason: str) -> tuple[bool, str, str | None]:
    """
    Reflect on a criterion evaluation. Returns (approved: bool, feedback: str, suggested_decision: str | None).
    If approved, suggested_decision is None. If revise, suggested_decision may be Y or N.
    """
    prompt = build_reflection_prompt(
        criterion_id, criterion_description, paper_text, decision, reason
    )
    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content="Review the screener's decision above."),
    ]
    result = model.invoke(messages)
    text = result.content if hasattr(result, 'content') else str(result)

    approved = "APPROVED" in text.upper()
    suggested = None
    if not approved and "REVISE" in text.upper():
        if "Y" in text.upper() and "N" in text.upper():
            # Try to extract suggested decision
            if "should be Y" in text.lower() or "correct decision is Y" in text.lower():
                suggested = "Y"
            elif "should be N" in text.lower() or "correct decision is N" in text.lower():
                suggested = "N"

    return approved, text[:300], suggested
