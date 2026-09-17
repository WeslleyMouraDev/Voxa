import uuid
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field

from backend.models.enums import TranscriptionMode


class ModeConfig(BaseModel):
    min_seconds: float
    max_seconds: float


def get_default_transcription_modes() -> dict[str, ModeConfig]:
    return {
        "normal": ModeConfig(min_seconds=4.0, max_seconds=6.0),
        "dynamic": ModeConfig(min_seconds=2.0, max_seconds=4.0),
        "accelerated": ModeConfig(min_seconds=1.0, max_seconds=2.0),
    }


class SettingsSchema(BaseModel):
    cpu_percent: int = Field(default=75, ge=25, le=100)
    server_port: int = 7865
    auto_open_browser: bool = True
    whisper_model: str = "medium"
    transcription_modes: dict[str, ModeConfig] = Field(
        default_factory=get_default_transcription_modes
    )


class VoiceSchema(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    sample_path: str
    is_default: bool = False
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class HistoryItemSchema(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    voice_id: str
    voice_name: str
    mode: Optional[TranscriptionMode] = None
    audio_path: str
    srt_path: Optional[str] = None
    duration_seconds: float = 0.0
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class NarrationRequestSchema(BaseModel):
    text: str
    voice_id: Optional[str] = None


class TranscriptionRequestSchema(BaseModel):
    audio_path: Optional[str] = None
    mode: TranscriptionMode = TranscriptionMode.NORMAL


class NarrationAndTranscriptionRequestSchema(BaseModel):
    text: str
    voice_id: Optional[str] = None
    mode: TranscriptionMode = TranscriptionMode.NORMAL
