import os

from dotenv import load_dotenv
from google import genai

load_dotenv()


class GeminiClient:
    """
    Wrapper around the Google Gemini API.
    """

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. Please check your .env file."
            )

        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-2.5-flash"
        )

        self.client = genai.Client(
            api_key=api_key
        )

    def _generate(self, prompt: str) -> str:
        """
        Send a prompt to Gemini and return the response text.
        """

        try:

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )

            text = response.text

            if text is None:
                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            return text.strip()

        except Exception as e:
            raise RuntimeError(
                f"Gemini API Error: {e}"
            ) from e

    def generate_sql(self, prompt: str) -> str:
        return self._generate(prompt)

    def generate_insights(self, prompt: str) -> str:
        return self._generate(prompt)

    def summarize_dataframe(self, prompt: str) -> str:
        return self._generate(prompt)