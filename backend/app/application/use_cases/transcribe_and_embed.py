from typing import Dict, Any, List

from app.application.interfaces.media import ITranscriber
from app.application.interfaces.llm import IEmbeddingService


class TranscribeAndEmbedUseCase:
    def __init__(self, transcriber: ITranscriber, embedder: IEmbeddingService):
        self.transcriber = transcriber
        self.embedder = embedder

    def execute(self, audio_path: str) -> Dict[str, Any]:
        text = self.transcriber.transcribe(audio_path)
        vectors: List[List[float]] = self.embedder.embed([text])
        return {"text": text, "embedding": vectors[0] if vectors else []}
