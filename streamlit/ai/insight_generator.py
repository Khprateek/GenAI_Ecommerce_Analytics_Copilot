from ai.gemini_client import GeminiClient


class InsightGenerator:

    def __init__(self):

        self.client = GeminiClient()

    def generate(self, dataframe_text):

        prompt = f"""
You are a Senior Business Analyst.

Analyze this dataset.

{dataframe_text}

Provide:

1. Key insights

2. Trends

3. Risks

4. Recommendations
"""

        return self.client.generate_insights(prompt)