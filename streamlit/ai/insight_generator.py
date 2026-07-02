from ai.gemini_client import GeminiClient
from ai.prompt_builder import PromptBuilder


class InsightGenerator:

    def __init__(self):
        self.client = GeminiClient()

    def generate(self, question, dataframe):

        prompt = PromptBuilder.build_insight_prompt(
            question,
            dataframe.to_markdown(index=False)
        )

        return self.client.generate_insights(prompt)