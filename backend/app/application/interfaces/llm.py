from typing import Protocol, List


class ILLMClient(Protocol):
    def chat(self, messages: List[dict]) -> str:
        """Send a chat conversation to the model and return a string response."""


class IEmbeddingService(Protocol):
    def embed(self, texts: List[str]) -> List[List[float]]:
        """Return embeddings for a list of texts."""
