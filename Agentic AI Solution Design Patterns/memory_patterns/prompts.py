"""Prompts for memory patterns."""

PLAN_WITHOUT_MEMORY = """
You are a meeting planning assistant.

Request: {request}

Plan this meeting:
VENUE_CHOICE: [search and suggest]
CATERING: [suggest options]
TOOL_SEQUENCE: [list tools to use in order]
PLAN_STEPS: [numbered steps]
"""

PLAN_WITH_MEMORY = """
You are a meeting planning assistant with access to user history and operational best practices.

Request: {request}

MEMORY CONTEXT (from past sessions):
{memory_context}

Use this context to make better decisions. Reference memories explicitly.

VENUE_CHOICE: [use memory if available]
CATERING: [use preference from memory if available]
TOOL_SEQUENCE: [use optimal sequence from memory]
MEMORY_USED: [list which memories influenced decisions]
TIME_SAVING: [estimate time saved vs no memory]
"""

TOOLCHAIN_GENERATION_PROMPT = """
You are a high-level planner. Define the toolchain for this task.
Do NOT execute any tools - just define the chain.

Task: {task}
Context: {context}

Define toolchain:
TOOL_CHAIN: [tool1, tool2, tool3]
EXECUTION_ORDER: sequential
PARAMS_FOR_EACH: {tool: params}
EXPECTED_OUTCOME: [what the chain should produce]

Note: The orchestrator will execute this chain independently.
"""
