"""
Prompts for Coherent State and Collective Memory pattern.
"""

AGENT_DECISION_PROMPT = """
You are a {agent_type} agent in a warehouse order fulfillment system.

Your private memory:
{private_memory}

{shared_memory_context}

Current task:
{task}

Make your decision and specify in this format:
ACTION: [what you will do]
STATE_UPDATE: [what to write to shared/private memory - key and value]
REASONING: [why this decision]
NEXT_STEP: [what should happen after this]
"""

NO_SHARED_MEMORY_CONTEXT = """
Note: You have NO access to shared memory.
You only know what's in your private memory.
You cannot see what other agents have done.
"""

SHARED_MEMORY_CONTEXT = """
Current shared memory state (what other agents have written):
{shared_state}

Use this to coordinate. Read before acting. Write your updates.
"""
