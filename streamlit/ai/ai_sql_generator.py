from ai.prompts import SYSTEM_PROMPT
from ai.gemini_client import GeminiClient


class SQLGenerator:

    def __init__(self):

        self.client = GeminiClient()

    def generate(self, question: str):

        prompt = f"""
{SYSTEM_PROMPT}

User Question

{question}

Return SQL only.
"""

        return self.client.generate_sql(prompt)