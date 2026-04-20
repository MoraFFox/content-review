"""Whisper audio transcription service."""

import whisper
from banshield.config import settings


class WhisperService:
    """Service for transcribing audio from video files."""

    def __init__(self) -> None:
        self.model = whisper.load_model(settings.whisper_model)

    def transcribe(self, audio_path: str) -> dict:
        """Transcribe audio file to text."""
        raise NotImplementedError
