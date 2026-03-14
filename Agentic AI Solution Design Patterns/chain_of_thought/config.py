"""
Chain of Thought — API Configuration and Constants

Configuration for Anthropic Claude API and the event planning scenario.
"""

MODEL = "claude-3-5-sonnet-20241022"
MAX_TOKENS = 1000

# Alternative: claude-3-opus-20240229, claude-opus-4-6 (if available)

USER_REQUEST = """
Plan a half-day team offsite meeting for next month.
Requirements:
- In-person
- Engaging activities
- Catering for 15 people
- Team must be available
"""
