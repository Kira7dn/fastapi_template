from fastapi import Depends

from app.core.config import settings

from app.application.use_cases.transcribe_and_embed import TranscribeAndEmbedUseCase
from app.infrastructure.adapters.llm import OpenAIChatClient, OpenAIEmbeddingClient
from app.infrastructure.adapters.transcriber import WhisperTranscriber


def get_transcriber():
    return WhisperTranscriber(settings.WHISPER_MODEL)


def get_embedder():
    return OpenAIEmbeddingClient(settings.OPENAI_API_KEY, settings.OPENAI_EMBED_MODEL)


def get_chat_client():
    return OpenAIChatClient(settings.OPENAI_API_KEY, settings.OPENAI_CHAT_MODEL)


def get_transcribe_and_embed_usecase(
    transcriber=Depends(get_transcriber),
    embedder=Depends(get_embedder),
) -> TranscribeAndEmbedUseCase:
    return TranscribeAndEmbedUseCase(transcriber, embedder)
