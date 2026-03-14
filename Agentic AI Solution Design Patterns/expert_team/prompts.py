"""
Prompts for Specialized Expert Team — breach response.
"""

EXPERT_ANALYSIS_PROMPT = """
You are a {domain} expert responding to a cybersecurity incident.

Your expertise areas: {expertise_areas}

Incident details:
{incident}

Provide your initial expert analysis in this format:

DOMAIN_ASSESSMENT: [Your domain-specific assessment]
KEY_FINDINGS: [List your most important findings, one per line]
IMMEDIATE_CONCERNS: [What worries you most]
RECOMMENDATIONS: [Your domain-specific recommendations]
NEEDS_INPUT_FROM: [Which other experts' input do you need]
CONFIDENCE: [0.0 to 1.0]
"""

PEER_RESPONSE_PROMPT = """
You are a {domain} expert.

Your previous analysis:
{my_analysis}

Other experts have shared these findings:
{peer_messages}

Respond to your peers. Be specific - challenge or support concrete findings.

For each finding you AGREE with:
SUPPORT: [expert_id] - [finding] - [why you agree]

For each finding you CHALLENGE or disagree with:
CHALLENGE: [expert_id] - [finding] - [why you disagree]

NEW_FINDING: [anything new you realized from peer input]

UPDATED_RECOMMENDATIONS: [how your recommendations changed based on peer input]
"""

CONSENSUS_PROMPT = """
You are synthesizing findings from a cybersecurity expert team.

Expert analyses:
{all_analyses}

Collaboration rounds:
{collaboration_rounds}

Build final consensus response in this format:

AGREED_FINDINGS: [points all experts agreed on]
RESOLVED_DISPUTES: [disputes that were resolved and how]
REMAINING_DISAGREEMENTS: [any unresolved points]

IMMEDIATE_ACTIONS: [Next 1-6 hours - numbered list]
SHORT_TERM_ACTIONS: [Next 24-72 hours - numbered list]
LEGAL_OBLIGATIONS: [Required legal actions with deadlines]
COMMUNICATION_PLAN: [Who to notify, when, how]
CONTAINMENT_STRATEGY: [Technical containment steps]

CONFIDENCE: [0.0 to 1.0 in this consensus]
"""
