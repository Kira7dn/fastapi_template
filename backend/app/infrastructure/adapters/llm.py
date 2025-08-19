from typing import List

from app.application.interfaces.llm import ILLMClient, IEmbeddingService


class OpenAIEmbeddingClient(IEmbeddingService):
    """Stub embedding client.
    Replace with real SDK calls when ready.
    """

    def __init__(self, api_key: str | None, model: str = "text-embedding-3-small"):
        self.api_key = api_key
        self.model = model

    def embed(self, texts: List[str]) -> List[List[float]]:
        # Stub: return deterministic fake vectors based on text length
        return [[float(len(t)), 0.0, 1.0] for t in texts]


class OpenAIChatClient(ILLMClient):
    """Stub chat client.
    Replace with real SDK calls when ready.
    """

    def __init__(self, api_key: str | None, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model

    def chat(self, messages: List[dict]) -> str:
        # Stub: echo last user message content
        for m in reversed(messages):
            if m.get("role") == "user":
                return f"[stub-{self.model}] {m.get('content', '')}"
        return f"[stub-{self.model}]"
