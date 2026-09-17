import io
from pathlib import Path
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient

from backend.models.enums import TranscriptionMode, TaskStatus
from backend.models.schemas import HistoryItemSchema, SettingsSchema, VoiceSchema
from backend.services.srt_builder import WordTimestamp
from backend.storage.settings_store import SettingsStore
from backend.storage.voice_store import VoiceStore
from backend.storage.history_store import HistoryStore
from backend.services.task_manager import TaskManager


@pytest.fixture
def test_env(tmp_path, monkeypatch):
    """
    Configura ambiente isolado com diretórios e stores temporários para a API.
    """
    data_dir = tmp_path / "data"
    voices_dir = tmp_path / "voices"
    output_dir = tmp_path / "output"
    data_dir.mkdir(parents=True, exist_ok=True)
    voices_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    settings_file = data_dir / "settings.json"
    voices_file = data_dir / "voices.json"
    history_file = data_dir / "history.json"

    # Patch nos caminhos de config
    monkeypatch.setattr("backend.config.DATA_DIR", data_dir)
    monkeypatch.setattr("backend.config.VOICES_DIR", voices_dir)
    monkeypatch.setattr("backend.config.OUTPUT_DIR", output_dir)
    monkeypatch.setattr("backend.config.SETTINGS_FILE", settings_file)
    monkeypatch.setattr("backend.config.VOICES_FILE", voices_file)
    monkeypatch.setattr("backend.config.HISTORY_FILE", history_file)

    # Cria stores limpos usando os arquivos temporários
    mock_settings_store = SettingsStore(file_path=settings_file)
    mock_voice_store = VoiceStore(file_path=voices_file)
    mock_history_store = HistoryStore(file_path=history_file)
    mock_task_manager = TaskManager()

    # Importa a app e faz monkeypatch nos singletons
    import backend.main as main_module
    import backend.routers.settings as r_settings
    import backend.routers.voices as r_voices
    import backend.routers.history as r_history
    import backend.routers.narration as r_narration
    import backend.routers.transcription as r_transcription
    import backend.routers.progress as r_progress

    for mod in [r_settings, main_module]:
        if hasattr(mod, "settings_store"):
            monkeypatch.setattr(mod, "settings_store", mock_settings_store)

    for mod in [r_voices, r_narration, main_module]:
        if hasattr(mod, "voice_store"):
            monkeypatch.setattr(mod, "voice_store", mock_voice_store)
        if hasattr(mod, "VOICES_DIR"):
            monkeypatch.setattr(mod, "VOICES_DIR", voices_dir)

    for mod in [r_history, r_narration, r_transcription, main_module]:
        if hasattr(mod, "history_store"):
            monkeypatch.setattr(mod, "history_store", mock_history_store)
        if hasattr(mod, "OUTPUT_DIR"):
            monkeypatch.setattr(mod, "OUTPUT_DIR", output_dir)

    for mod in [r_narration, r_transcription, r_progress, main_module]:
        if hasattr(mod, "task_manager"):
            monkeypatch.setattr(mod, "task_manager", mock_task_manager)

    test_app = main_module.create_app()
    client = TestClient(test_app)
    return {
        "client": client,
        "app": test_app,
        "settings_store": mock_settings_store,
        "voice_store": mock_voice_store,
        "history_store": mock_history_store,
        "task_manager": mock_task_manager,
        "voices_dir": voices_dir,
        "output_dir": output_dir,
        "tmp_path": tmp_path,
    }


# ==============================================================================
# 1. Testes de Settings (/api/settings)
# ==============================================================================

def test_get_settings(test_env):
    client = test_env["client"]
    res = client.get("/api/settings")
    assert res.status_code == 200
    data = res.json()
    assert "cpu_percent" in data
    assert data["cpu_percent"] == 75
    assert data["server_port"] == 7865
    assert "transcription_modes" in data


def test_update_settings(test_env):
    client = test_env["client"]
    payload = {
        "cpu_percent": 50,
        "server_port": 8000,
        "auto_open_browser": False,
        "whisper_model": "base",
        "transcription_modes": {
            "normal": {"min_seconds": 3.0, "max_seconds": 5.0},
            "dynamic": {"min_seconds": 1.5, "max_seconds": 3.0},
            "accelerated": {"min_seconds": 0.5, "max_seconds": 1.5},
        },
    }
    with patch("backend.services.cpu_limiter.CPULimiter.apply_limits") as mock_apply:
        res = client.put("/api/settings", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["cpu_percent"] == 50
        assert data["server_port"] == 8000
        assert data["auto_open_browser"] is False
        assert data["whisper_model"] == "base"
        mock_apply.assert_called_once_with(50)


# ==============================================================================
# 2. Testes de Voices (/api/voices)
# ==============================================================================

def test_list_voices_empty(test_env):
    client = test_env["client"]
    res = client.get("/api/voices")
    assert res.status_code == 200
    assert res.json() == []


def test_create_voice_upload(test_env):
    client = test_env["client"]
    audio_bytes = b"RIFFfake_wav_audio_content"
    files = {"file": ("locutor_br.wav", io.BytesIO(audio_bytes), "audio/wav")}
    data = {"name": "Locutor BR", "is_default": "true"}

    res = client.post("/api/voices", data=data, files=files)
    assert res.status_code == 201
    voice_data = res.json()
    assert voice_data["name"] == "Locutor BR"
    assert voice_data["is_default"] is True
    assert "sample_path" in voice_data
    assert Path(voice_data["sample_path"]).exists()

    # Verifica se aparece na listagem
    list_res = client.get("/api/voices")
    assert len(list_res.json()) == 1


def test_set_default_voice(test_env):
    client = test_env["client"]
    v_store = test_env["voice_store"]
    sample_p = test_env["voices_dir"] / "dummy1.wav"
    sample_p.write_bytes(b"123")
    v1 = v_store.add_voice("Voz 1", str(sample_p), is_default=True)
    v2 = v_store.add_voice("Voz 2", str(sample_p), is_default=False)

    # Define v2 como default
    res = client.put(f"/api/voices/{v2.id}/default")
    assert res.status_code == 200
    assert res.json()["is_default"] is True

    # 404 para ID inexistente
    res_404 = client.put("/api/voices/non-existent-id/default")
    assert res_404.status_code == 404


def test_delete_voice(test_env):
    client = test_env["client"]
    v_store = test_env["voice_store"]
    sample_p = test_env["voices_dir"] / "dummy_del.wav"
    sample_p.write_bytes(b"sample audio")
    v = v_store.add_voice("Voz Para Deletar", str(sample_p), is_default=False)

    res = client.delete(f"/api/voices/{v.id}")
    assert res.status_code == 200
    assert not sample_p.exists()

    # 404 para voz já excluída
    res_404 = client.delete(f"/api/voices/{v.id}")
    assert res_404.status_code == 404


# ==============================================================================
# 3. Testes de History (/api/history)
# ==============================================================================

def test_history_list_and_delete(test_env):
    client = test_env["client"]
    h_store = test_env["history_store"]
    out_dir = test_env["output_dir"]

    item_audio = out_dir / "item1.mp3"
    item_srt = out_dir / "item1.srt"
    item_audio.write_bytes(b"audio")
    item_srt.write_text("1\n00:00:01,000 --> 00:00:02,000\nTeste", encoding="utf-8")

    item = HistoryItemSchema(
        text="Histórico teste",
        voice_id="v1",
        voice_name="Locutor 1",
        audio_path=str(item_audio),
        srt_path=str(item_srt),
        duration_seconds=2.5,
    )
    h_store.add_item(item)

    # List
    res = client.get("/api/history")
    assert res.status_code == 200
    items = res.json()
    assert len(items) == 1
    assert items[0]["id"] == item.id

    # Delete individual
    del_res = client.delete(f"/api/history/{item.id}")
    assert del_res.status_code == 200
    assert not item_audio.exists()
    assert not item_srt.exists()

    # 404 para item já removido
    assert client.delete(f"/api/history/{item.id}").status_code == 404


def test_clear_all_history(test_env):
    client = test_env["client"]
    h_store = test_env["history_store"]
    out_dir = test_env["output_dir"]

    for i in range(3):
        f_mp3 = out_dir / f"f_{i}.mp3"
        f_mp3.write_bytes(b"content")
        h_store.add_item(
            HistoryItemSchema(
                text=f"Text {i}",
                voice_id="v",
                voice_name="V",
                audio_path=str(f_mp3),
            )
        )

    assert len(h_store.list_history()) == 3
    res = client.delete("/api/history")
    assert res.status_code == 200
    assert res.json()["deleted_count"] == 3
    assert len(h_store.list_history()) == 0


# ==============================================================================
# 4. Testes de Narration (/api/narrate e /api/narrate-and-transcribe)
# ==============================================================================

def test_narrate_no_voices_returns_400(test_env):
    client = test_env["client"]
    res = client.post("/api/narrate", json={"text": "Olá mundo"})
    assert res.status_code == 400
    assert "voz" in res.json()["detail"].lower()


def test_narrate_success_dispatches_task(test_env):
    client = test_env["client"]
    v_store = test_env["voice_store"]
    sample_p = test_env["voices_dir"] / "locutor.wav"
    sample_p.write_bytes(b"sample")
    voice = v_store.add_voice("Locutor Oficial", str(sample_p), is_default=True)

    with patch("backend.services.tts_service.TTSService.generate_speech") as mock_gen:
        def fake_gen(text, voice_sample_path, output_mp3_path, progress_callback=None):
            Path(output_mp3_path).write_bytes(b"fake_mp3_audio")
            if progress_callback:
                progress_callback(100.0, "Concluído")
            return Path(output_mp3_path)

        mock_gen.side_effect = fake_gen

        res = client.post("/api/narrate", json={"text": "Texto para narrar", "voice_id": voice.id})
        assert res.status_code == 202
        task_id = res.json()["task_id"]
        assert task_id

        # Verifica tarefa no TaskManager
        tm = test_env["task_manager"]
        task = tm.get_task(task_id)
        assert task is not None
        assert task["status"] == TaskStatus.COMPLETED
        assert "audio_url" in task["result"]


def test_narrate_and_transcribe_no_voices_returns_400(test_env):
    client = test_env["client"]
    res = client.post("/api/narrate-and-transcribe", json={"text": "Olá", "mode": "dynamic"})
    assert res.status_code == 400


def test_narrate_and_transcribe_success(test_env):
    client = test_env["client"]
    v_store = test_env["voice_store"]
    sample_p = test_env["voices_dir"] / "locutor.wav"
    sample_p.write_bytes(b"sample")
    voice = v_store.add_voice("Locutor Oficial", str(sample_p), is_default=True)

    with patch("backend.services.tts_service.TTSService.generate_speech") as mock_tts, \
         patch("backend.services.stt_service.STTService.transcribe_audio") as mock_stt:

        def fake_tts(text, voice_sample_path, output_mp3_path, progress_callback=None):
            Path(output_mp3_path).write_bytes(b"mp3_data")
            return Path(output_mp3_path)

        def fake_stt(audio_path, mode=TranscriptionMode.NORMAL, mode_config=None, progress_callback=None):
            return "1\n00:00:00,000 --> 00:00:02,000\nTexto narrado", [
                WordTimestamp(word="Texto", start=0.0, end=1.0, probability=0.99),
                WordTimestamp(word="narrado", start=1.0, end=2.0, probability=0.98),
            ], 2.0

        mock_tts.side_effect = fake_tts
        mock_stt.side_effect = fake_stt

        res = client.post(
            "/api/narrate-and-transcribe",
            json={"text": "Texto narrado", "mode": "dynamic"},
        )
        assert res.status_code == 202
        task_id = res.json()["task_id"]

        tm = test_env["task_manager"]
        task = tm.get_task(task_id)
        assert task is not None
        assert task["status"] == TaskStatus.COMPLETED
        assert "audio_url" in task["result"]
        assert "srt_url" in task["result"]


# ==============================================================================
# 5. Testes de Transcription (/api/transcribe)
# ==============================================================================

def test_transcribe_missing_inputs_returns_400(test_env):
    client = test_env["client"]
    res = client.post("/api/transcribe", data={"mode": "normal"})
    assert res.status_code == 400


def test_transcribe_with_audio_path_success(test_env):
    client = test_env["client"]
    audio_file = test_env["output_dir"] / "input_test.mp3"
    audio_file.write_bytes(b"input_mp3_bytes")

    with patch("backend.services.stt_service.STTService.transcribe_audio") as mock_stt:
        mock_stt.return_value = (
            "1\n00:00:00,000 --> 00:00:01,500\nFala transcrita",
            [WordTimestamp(word="Fala", start=0.0, end=0.7, probability=0.9),
             WordTimestamp(word="transcrita", start=0.8, end=1.5, probability=0.95)],
            1.5
        )

        res = client.post("/api/transcribe", data={"audio_path": str(audio_file), "mode": "accelerated"})
        assert res.status_code == 202
        task_id = res.json()["task_id"]

        tm = test_env["task_manager"]
        task = tm.get_task(task_id)
        assert task is not None
        assert task["status"] == TaskStatus.COMPLETED
        assert "srt_url" in task["result"]


def test_transcribe_with_file_upload_success(test_env):
    client = test_env["client"]
    audio_bytes = b"fake_uploaded_audio_file"
    files = {"file": ("input_upload.mp3", io.BytesIO(audio_bytes), "audio/mpeg")}
    data = {"mode": "normal"}

    with patch("backend.services.stt_service.STTService.transcribe_audio") as mock_stt:
        mock_stt.return_value = (
            "1\n00:00:00,000 --> 00:00:01,000\nUpload feito",
            [WordTimestamp(word="Upload", start=0.0, end=0.5, probability=0.9),
             WordTimestamp(word="feito", start=0.5, end=1.0, probability=0.9)],
            1.0
        )

        res = client.post("/api/transcribe", data=data, files=files)
        assert res.status_code == 202
        task_id = res.json()["task_id"]

        tm = test_env["task_manager"]
        task = tm.get_task(task_id)
        assert task is not None
        assert task["status"] == TaskStatus.COMPLETED
        assert "srt_url" in task["result"]


# ==============================================================================
# 6. Testes de Progress SSE (/api/progress/{task_id})
# ==============================================================================

def test_progress_not_found(test_env):
    client = test_env["client"]
    res = client.get("/api/progress/non-existent-task-id")
    assert res.status_code == 404


def test_progress_sse_stream(test_env):
    client = test_env["client"]
    tm = test_env["task_manager"]
    task_id = tm.create_task(name="Teste SSE")
    tm.complete_task(task_id, {"status": "ok"})

    res = client.get(f"/api/progress/{task_id}")
    assert res.status_code == 200
    assert "text/event-stream" in res.headers["content-type"]
    body = res.text
    assert "data:" in body
    assert task_id in body
    assert "completed" in body


# ==============================================================================
# 7. Testes de Arquivos Estáticos (/voices e /output)
# ==============================================================================

def test_static_files_serving(test_env):
    client = test_env["client"]
    # Arquivo em voices
    v_file = test_env["voices_dir"] / "test_sample.txt"
    v_file.write_text("conteúdo da voz", encoding="utf-8")

    res_voice = client.get("/voices/test_sample.txt")
    assert res_voice.status_code == 200
    assert res_voice.text == "conteúdo da voz"

    # Arquivo em output
    out_file = test_env["output_dir"] / "test_out.txt"
    out_file.write_text("conteúdo de saída", encoding="utf-8")

    res_out = client.get("/output/test_out.txt")
    assert res_out.status_code == 200
    assert res_out.text == "conteúdo de saída"
