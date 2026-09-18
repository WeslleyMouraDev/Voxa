import pytest
from pydantic import ValidationError

from backend.models.schemas import (
    HistoryItemSchema,
    LogEntrySchema,
    NarrationAndTranscriptionRequestSchema,
    NarrationRequestSchema,
    SystemMetricsSchema,
)


def test_narration_request_schema_defaults():
    req = NarrationRequestSchema(text="Olá mundo")
    assert req.speed == 1.0
    assert req.max_pause == 0.3
    assert req.pitch == 0.0
    assert req.presence == 0.5


@pytest.mark.parametrize(
    "field,invalid_val",
    [
        ("speed", 0.4),
        ("speed", 2.1),
        ("max_pause", -0.1),
        ("max_pause", 2.1),
        ("pitch", -12.1),
        ("pitch", 12.1),
        ("presence", -0.1),
        ("presence", 1.1),
    ],
)
def test_narration_request_schema_validation(field, invalid_val):
    with pytest.raises(ValidationError):
        NarrationRequestSchema(text="Olá", **{field: invalid_val})


def test_narration_and_transcription_request_schema_defaults():
    req = NarrationAndTranscriptionRequestSchema(text="Olá mundo")
    assert req.speed == 1.0
    assert req.max_pause == 0.3
    assert req.pitch == 0.0
    assert req.presence == 0.5


@pytest.mark.parametrize(
    "field,invalid_val",
    [
        ("speed", 0.4),
        ("speed", 2.1),
        ("max_pause", -0.1),
        ("max_pause", 2.1),
        ("pitch", -12.1),
        ("pitch", 12.1),
        ("presence", -0.1),
        ("presence", 1.1),
    ],
)
def test_narration_and_transcription_request_schema_validation(field, invalid_val):
    with pytest.raises(ValidationError):
        NarrationAndTranscriptionRequestSchema(text="Olá", **{field: invalid_val})


def test_history_item_schema_controls_defaults():
    item = HistoryItemSchema(
        text="Histórico",
        voice_id="v1",
        voice_name="Voz Teste",
        audio_path="/tmp/audio.wav",
    )
    assert item.speed == 1.0
    assert item.max_pause == 0.3
    assert item.pitch == 0.0
    assert item.presence == 0.5


def test_history_item_schema_controls_custom():
    item = HistoryItemSchema(
        text="Histórico",
        voice_id="v1",
        voice_name="Voz Teste",
        audio_path="/tmp/audio.wav",
        speed=1.5,
        max_pause=0.8,
        pitch=2.0,
        presence=0.9,
    )
    assert item.speed == 1.5
    assert item.max_pause == 0.8
    assert item.pitch == 2.0
    assert item.presence == 0.9


def test_log_entry_schema():
    log = LogEntrySchema(
        id=1,
        timestamp="2026-09-18T12:00:00Z",
        level="INFO",
        message="Processamento iniciado",
    )
    assert log.id == 1
    assert log.timestamp == "2026-09-18T12:00:00Z"
    assert log.level == "INFO"
    assert log.message == "Processamento iniciado"
    assert log.source == "app"


def test_system_metrics_schema():
    metrics = SystemMetricsSchema(
        cpu_percent=45.5,
        ram_used_gb=8.2,
        ram_total_gb=16.0,
        ram_percent=51.25,
    )
    assert metrics.cpu_percent == 45.5
    assert metrics.ram_used_gb == 8.2
    assert metrics.ram_total_gb == 16.0
    assert metrics.ram_percent == 51.25
