from typing import Any
from orionmentor.config import settings

# Installare openai se lo usi: pip install openai
try:
    from openai import OpenAI
except Exception:
    OpenAI = None

class OpenAIProvider:
    name = "openai"
    def __init__(self, model: str):
        self.model = model
        if OpenAI is None:
            raise ImportError("openai sdk not installed. pip install openai")
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def invoke(self, prompt: str) -> Any:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt}
                ],
            }],
        )
        return resp.choices[0].message.content
