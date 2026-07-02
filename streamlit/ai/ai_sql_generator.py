from ai.gemini_client import GeminiClient
from ai.prompt_builder import PromptBuilder


class SQLGenerator:

    def __init__(self):
        self.client = GeminiClient()

    def generate(self, question: str) -> str:

        prompt = PromptBuilder.build_sql_prompt(question)

        return self.client.generate_sql(prompt)