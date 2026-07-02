from ai.prompts import SYSTEM_PROMPT
from ai.schema_context import WAREHOUSE_CONTEXT


class PromptBuilder:

    @staticmethod
    def build_sql_prompt(question: str) -> str:
        return f"""
{SYSTEM_PROMPT}

==========================================================

WAREHOUSE SCHEMA

{WAREHOUSE_CONTEXT}

==========================================================

USER QUESTION

{question}

==========================================================

Instructions

Generate valid BigQuery Standard SQL.

Use ONLY the tables and columns defined in the warehouse schema.

Use joins only when necessary.

Return SQL only.

Do not explain the SQL.

Do not use markdown.

Do not surround SQL with triple backticks.
"""

    @staticmethod
    def build_insight_prompt(question: str, dataframe_markdown: str) -> str:
        return f"""
You are a Senior Business Intelligence Analyst.

The user asked:

{question}

SQL Result

{dataframe_markdown}

Write a concise executive summary.

Include:

1. Key findings

2. Business trends

3. Opportunities

4. Risks

5. Recommendations

Limit the response to approximately 200 words.

Do not mention SQL.
"""