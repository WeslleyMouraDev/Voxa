import os
import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import pytest

from backend.models.enums import TranscriptionMode, TaskStatus
from backend.models.schemas import (
    ModeConfig,
    SettingsSchema,
    VoiceSchema,
    HistoryItemSchema,
    NarrationRequestSchema,
    TranscriptionRequestSchema,
    NarrationAndTranscriptionRequestSchema,
)
from backend.storage.json_store import JSONStore
from backend.storage.settings_store import SettingsStore
from backend.storage.voice_store import VoiceStore
from backend.storage.history_store import HistoryStore


def test_enums():
    assert TranscriptionMode.NORMAL.value == "normal"
    assert TranscriptionMode.DYNAMIC.value == "dynamic"
    assert TranscriptionMode.ACCELERATED.value == "accelerated"

    assert TaskStatus.IDLE.value == "idle"
    assert TaskStatus.PROCESSING.value == "processing"
    assert TaskStatus.COMPLETED.value == "completed"
    assert TaskStatus.ERROR.value == "error"


def test_schemas_defaults_and_validation():
    settings = SettingsSchema()
    assert settings.cpu_percent == 75
    assert settings.server_port == 7865
    assert settings.auto_open_browser is True
    assert settings.whisper_model == "medium"
    assert "normal" in settings.transcription_modes
    assert settings.transcription_modes["normal"].min_seconds == 4.0
    assert settings.transcription_modes["normal"].max_seconds == 6.0
    assert settings.transcription_modes["dynamic"].min_seconds == 2.0
    assert settings.transcription_modes["dynamic"].max_seconds == 4.0
    assert settings.transcription_modes["accelerated"].min_seconds == 1.0
    assert settings.transcription_modes["accelerated"].max_seconds == 2.0

    narr_req = NarrationRequestSchema(text="Hello")
    assert narr_req.text == "Hello"
    assert narr_req.voice_id is None

    transc_req = TranscriptionRequestSchema(audio_path="/tmp/audio.mp3")
    assert transc_req.audio_path == "/tmp/audio.mp3"
    assert transc_req.mode == TranscriptionMode.NORMAL

    both_req = NarrationAndTranscriptionRequestSchema(text="Hello", mode=TranscriptionMode.DYNAMIC)
    assert both_req.text == "Hello"
    assert both_req.voice_id is None
    assert both_req.mode == TranscriptionMode.DYNAMIC


def test_json_store_atomic_write_and_read(tmp_path):
    file_path = tmp_path / "test.json"
    store = JSONStore(file_path)

    initial_data = {"key": "value", "list": [1, 2, 3]}
    store.write(initial_data)

    assert file_path.exists()
    assert store.read() == initial_data

    # Corrupted content test
    file_path.write_text("invalid json content {{{", encoding="utf-8")
    assert store.read(default={"fallback": True}) == {"fallback": True}


def test_json_store_concurrency(tmp_path):
    file_path = tmp_path / "concurrent.json"
    store = JSONStore(file_path)
    store.write({"counter": 0})

    def increment_counter(_):
        with store.lock:
            data = store.read(default={"counter": 0})
            data["counter"] += 1
            time.sleep(0.001)
            store.write(data)

    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(increment_counter, range(30)))

    final_data = store.read()
    assert final_data["counter"] == 30


def test_settings_store_lifecycle(tmp_path):
    settings_file = tmp_path / "settings.json"
    store = SettingsStore(file_path=settings_file)

    # Initial load creates defaults and writes file
    settings = store.get_settings()
    assert settings.cpu_percent == 75
    assert settings.server_port == 7865
    assert settings_file.exists()

    # Update with dict
    updated = store.update_settings({"cpu_percent": 50, "whisper_model": "large"})
    assert updated.cpu_percent == 50
    assert updated.whisper_model == "large"
    assert store.get_settings().cpu_percent == 50

    # Update with schema
    new_schema = SettingsSchema(cpu_percent=90, server_port=8000)
    updated2 = store.update_settings(new_schema)
    assert updated2.cpu_percent == 90
    assert updated2.server_port == 8000
    assert store.get_settings().server_port == 8000

    # Corrupt file reload
    settings_file.write_text("corrupted!!!", encoding="utf-8")
    restored = store.get_settings()
    assert restored.cpu_percent == 75


def test_voice_store_lifecycle(tmp_path):
    voices_file = tmp_path / "voices.json"
    store = VoiceStore(file_path=voices_file)

    sample1 = tmp_path / "v1.mp3"
    sample2 = tmp_path / "v2.mp3"
    sample3 = tmp_path / "v3.mp3"
    sample1.write_text("audio1")
    sample2.write_text("audio2")
    sample3.write_text("audio3")

    assert store.list_voices() == []
    assert store.get_default_voice() is None

    # First voice automatically becomes default
    v1 = store.add_voice(name="Voice 1", sample_path=str(sample1))
    assert v1.is_default is True
    assert store.get_default_voice().id == v1.id

    # Second voice without is_default stays False
    v2 = store.add_voice(name="Voice 2", sample_path=str(sample2), is_default=False)
    assert v2.is_default is False
    assert store.get_default_voice().id == v1.id

    # Third voice with is_default=True unsets previous default
    v3 = store.add_voice(name="Voice 3", sample_path=str(sample3), is_default=True)
    assert v3.is_default is True
    assert store.get_default_voice().id == v3.id
    assert store.get_voice(v1.id).is_default is False

    # set_default_voice switch
    assert store.set_default_voice(v2.id) is True
    assert store.get_default_voice().id == v2.id
    assert store.get_voice(v3.id).is_default is False

    # Delete default voice with physical file deletion
    assert sample2.exists()
    assert store.delete_voice(v2.id, delete_file=True) is True
    assert not sample2.exists()

    # First remaining voice becomes default (v1)
    new_def = store.get_default_voice()
    assert new_def is not None
    assert new_def.id == v1.id

    # Delete non-default or default without file deletion
    assert sample1.exists()
    assert store.delete_voice(v1.id, delete_file=False) is True
    assert sample1.exists()

    # Now only v3 remains and is default
    remaining = store.list_voices()
    assert len(remaining) == 1
    assert remaining[0].id == v3.id
    assert store.get_default_voice().id == v3.id

    # Delete last voice
    assert store.delete_voice(v3.id, delete_file=True) is True
    assert store.list_voices() == []
    assert store.get_default_voice() is None


def test_history_store_lifecycle(tmp_path):
    history_file = tmp_path / "history.json"
    store = HistoryStore(file_path=history_file)

    assert store.list_history() == []

    audio1 = tmp_path / "a1.mp3"
    srt1 = tmp_path / "a1.srt"
    audio2 = tmp_path / "a2.mp3"
    srt2 = tmp_path / "a2.srt"
    audio1.write_text("mp3-1")
    srt1.write_text("srt-1")
    audio2.write_text("mp3-2")
    srt2.write_text("srt-2")

    item1 = HistoryItemSchema(
        id="item-1",
        text="Text 1",
        voice_id="v1",
        voice_name="Voice 1",
        mode=TranscriptionMode.NORMAL,
        audio_path=str(audio1),
        srt_path=str(srt1),
        duration_seconds=5.0,
        created_at="2026-09-17T10:00:00Z",
    )
    item2 = HistoryItemSchema(
        id="item-2",
        text="Text 2",
        voice_id="v2",
        voice_name="Voice 2",
        mode=TranscriptionMode.DYNAMIC,
        audio_path=str(audio2),
        srt_path=str(srt2),
        duration_seconds=3.0,
        created_at="2026-09-17T11:00:00Z",
    )

    store.add_item(item1)
    store.add_item(item2)

    # list_history must be sorted by created_at descending (item2 first)
    history = store.list_history()
    assert len(history) == 2
    assert history[0].id == "item-2"
    assert history[1].id == "item-1"

    # get_item
    assert store.get_item("item-1").text == "Text 1"
    assert store.get_item("non-existent") is None

    # delete_item with file deletion
    assert audio1.exists()
    assert srt1.exists()
    assert store.delete_item("item-1", delete_files=True) is True
    assert not audio1.exists()
    assert not srt1.exists()
    assert len(store.list_history()) == 1

    # clear_all with file deletion
    assert audio2.exists()
    assert srt2.exists()
    count = store.clear_all(delete_files=True)
    assert count == 1
    assert not audio2.exists()
    assert not srt2.exists()
    assert store.list_history() == []
