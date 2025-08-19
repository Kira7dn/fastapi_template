from typing import Protocol, List


class ITranscriber(Protocol):
    def transcribe(self, audio_path: str) -> str:
        """Transcribe an audio file into text."""


class IMediaProcessor(Protocol):
    def extract_frames(self, video_path: str, fps: int) -> List[str]:
        """Extract frames from a video and return list of frame file paths."""
