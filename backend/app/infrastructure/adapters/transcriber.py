from app.application.interfaces.media import ITranscriber


class WhisperTranscriber(ITranscriber):
    """Stub transcriber. Replace with real Whisper/local ASR integration."""

    def __init__(self, model: str = "base"):
        self.model = model

    def transcribe(self, audio_path: str) -> str:
        # Stub: return a fake transcription derived from the filename
        return f"[stub-{self.model}] transcribed {audio_path}"
