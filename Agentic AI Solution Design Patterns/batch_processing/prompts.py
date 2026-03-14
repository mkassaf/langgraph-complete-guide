"""
Prompts for batch processing agents.
"""

DATA_VALIDATION_PROMPT = """
You are a data collection agent validating customer records.

Records to submit (showing first 5 of {total}):
{sample_records}

Validate batch quality:
VALID_RECORDS: [count]
MESSY_RECORDS: [count]
CRITICAL_ISSUES: [any show-stoppers]
SUBMIT_TO_BATCH: yes/no
BATCH_NOTES: [any preprocessing notes]
"""

CLEANSING_PROMPT = """
You are a data cleansing agent.

Received batch of {count} records to clean:
{batch_sample}

For each record identify and fix:
ISSUES_FOUND: [list of data quality problems]
FIXES_APPLIED: [what was corrected]
RECORDS_CLEANED: [count]
RECORDS_REJECTED: [count] (unfixable)
CLEANSING_SUMMARY: [overall quality assessment]
OUTPUT: cleaned batch ready for analysis
"""

ANALYSIS_PROMPT = """
You are a data analysis agent.

Received batch of {count} clean customer records:
{batch_data}

Perform analytics:
TOTAL_REVENUE: [sum]
TOP_CUSTOMERS: [top 3 by purchase amount]
CATEGORY_BREAKDOWN: [revenue by category]
PURCHASE_PATTERNS: [notable patterns]
CUSTOMER_SEGMENTS: [high/medium/low value]
ANOMALIES: [anything unusual]
INSIGHTS: [key business insights]
"""

REPORT_PROMPT = """
You are a business report generation agent.

Analysis results batch ({count} analyses):
{analyses}

Generate executive report:
EXECUTIVE_SUMMARY: [key findings in 3 bullets]
REVENUE_HIGHLIGHTS: [top metrics]
CUSTOMER_INSIGHTS: [customer behavior findings]
RECOMMENDATIONS: [actionable next steps]
RISK_FLAGS: [any concerns]
REPORT_DATE: {date}
"""

LEARNING_BATCH_PROMPT = """
You are a learning microservice processing a batch of
processing steps from one agent cycle.

Processing steps in this batch:
{steps}

Extract learnings:
PERCEPTION_LEARNINGS: [what to improve in detection]
REASONING_LEARNINGS: [what to improve in decisions]
ACTION_LEARNINGS: [what to improve in execution]
OVERALL_IMPROVEMENT: [key lesson from this cycle]
MODEL_UPDATES_NEEDED: [what parameters to adjust]
"""

SYNC_PROMPT = """
You are a state synchronization agent.

Received batch of {count} state updates to apply:
{updates}

Apply to shared memory:
UPDATES_APPLIED: [list of keys updated]
CONFLICTS_RESOLVED: [any merge conflicts]
SYNC_SUMMARY: [efficiency note - batch vs individual]
"""
