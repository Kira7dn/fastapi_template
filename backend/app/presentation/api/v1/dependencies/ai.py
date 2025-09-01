from fastapi import Depends

from app.core.config import settings

from app.application.interfaces.media import ITranscriber
from app.application.interfaces.llm import ILLMClient, IEmbeddingService
from app.application.use_cases.transcribe_and_embed import TranscribeAndEmbedUseCase
from app.infrastructure.adapters.llm import OpenAIChatClient, OpenAIEmbeddingClient
from app.infrastructure.adapters.transcriber import WhisperTranscriber


def get_transcriber() -> ITranscriber:
    return WhisperTranscriber(settings.WHISPER_MODEL)


def get_embedder() -> IEmbeddingService:
    return OpenAIEmbeddingClient(settings.OPENAI_API_KEY, settings.OPENAI_EMBED_MODEL)


def get_chat_client() -> ILLMClient:
    return OpenAIChatClient(settings.OPENAI_API_KEY, settings.OPENAI_CHAT_MODEL)


def get_transcribe_and_embed_usecase(
    transcriber: ITranscriber = Depends(get_transcriber),
    embedder: IEmbeddingService = Depends(get_embedder),
) -> TranscribeAndEmbedUseCase:
    return TranscribeAndEmbedUseCase(transcriber, embedder)
