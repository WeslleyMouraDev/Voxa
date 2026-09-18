import time
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from backend.main import create_app
from backend.models.enums import TaskStatus, TranscriptionMode
from backend.models.schemas import HistoryItemSchema
from backend.services.log_service import LogService, log_service
from backend.services.metrics_service import MetricsService
from backend.services.srt_builder import WordTimestamp
from backend.services.task_manager import TaskManager
from backend.storage.history_store import HistoryStore
from backend.storage.settings_store import SettingsStore
from backend.storage.voice_store import VoiceStore


@pytest.fixture
def client_env(tmp_path, monkeypatch):
    """
    Ambiente isolado para testes dos endpoints de logs, métricas e narração.
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

    monkeypatch.setattr("backend.config.DATA_DIR", data_dir)
    monkeypatch.setattr("backend.config.VOICES_DIR", voices_dir)
    monkeypatch.setattr("backend.config.OUTPUT_DIR", output_dir)
    monkeypatch.setattr("backend.config.SETTINGS_FILE", settings_file)
    monkeypatch.setattr("backend.config.VOICES_FILE", voices_file)
    monkeypatch.setattr("backend.config.HISTORY_FILE", history_file)

    mock_settings_store = SettingsStore(file_path=settings_file)
    mock_voice_store = VoiceStore(file_path=voices_file)
    mock_history_store = HistoryStore(file_path=history_file)
    mock_task_manager = TaskManager()

    # Limpa o log_service singleton
    log_service.clear()

    import backend.main as main_module
    import backend.routers.history as r_history
    import backend.routers.narration as r_narration
    import backend.routers.progress as r_progress
    import backend.routers.settings as r_settings
    import backend.routers.transcription as r_transcription
    import backend.routers.voices as r_voices

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

    app = main_module.create_app()
    client = TestClient(app)
    return {
        "client": client,
        "app": app,
        "settings_store": mock_settings_store,
        "voice_store": mock_voice_store,
        "history_store": mock_history_store,
        "task_manager": mock_task_manager,
        "voices_dir": voices_dir,
        "output_dir": output_dir,
    }


# ==============================================================================
# 1. Testes de Logs REST (/api/logs)
# ==============================================================================

def test_get_logs_empty(client_env):
    client = client_env["client"]
    res = client.get("/api/logs")
    assert res.status_code == 200
    assert res.json() == []


def test_get_logs_with_filtering_and_limit(client_env):
    client = client_env["client"]
    log_service.add_log("INFO", "Sistema iniciado com sucesso", "system")
    log_service.add_log("WARNING", "Uso de memória elevado", "monitor")
    log_service.add_log("ERROR", "Falha ao ler arquivo de áudio", "tts")
    log_service.add_log("INFO", "Processamento de lote finalizado", "worker")

    # Sem filtros: todos os 4 logs
    res = client.get("/api/logs")
    assert res.status_code == 200
    assert len(res.json()) == 4

    # Filtro por level
    res_err = client.get("/api/logs?level=ERROR")
    assert res_err.status_code == 200
    data_err = res_err.json()
    assert len(data_err) == 1
    assert data_err[0]["level"] == "ERROR"
    assert "Falha" in data_err[0]["message"]

    # Filtro por search
    res_search = client.get("/api/logs?search=memória")
    assert res_search.status_code == 200
    data_search = res_search.json()
    assert len(data_search) == 1
    assert "elevado" in data_search[0]["message"]

    # Filtro por limit
    res_limit = client.get("/api/logs?limit=2")
    assert res_limit.status_code == 200
    data_limit = res_limit.json()
    assert len(data_limit) == 2
    assert data_limit[-1]["message"] == "Processamento de lote finalizado"


def test_get_logs_limit_validation(client_env):
    client = client_env["client"]
    # Limite zero ou negativo deve ser rejeitado pela validação do FastAPI
    res_zero = client.get("/api/logs?limit=0")
    assert res_zero.status_code == 422

    # Limite maior que 1000 deve ser rejeitado
    res_over = client.get("/api/logs?limit=1001")
    assert res_over.status_code == 422


def test_delete_logs(client_env):
    client = client_env["client"]
    log_service.add_log("INFO", "Mensagem 1", "test")
    log_service.add_log("INFO", "Mensagem 2", "test")
    assert len(log_service.get_logs()) == 2

    res = client.delete("/api/logs")
    assert res.status_code == 200
    assert res.json() == {"message": "Logs limpos com sucesso"}
    assert len(log_service.get_logs()) == 0


# ==============================================================================
# 2. Testes de Métricas de Sistema (/api/system/metrics)
# ==============================================================================

def test_get_system_metrics(client_env):
    client = client_env["client"]
    with patch("backend.services.metrics_service.MetricsService.get_current_metrics") as mock_metrics:
        mock_metrics.return_value = {
            "cpu_percent": 18.5,
            "ram_used_gb": 4.25,
            "ram_total_gb": 16.0,
            "ram_percent": 26.56,
        }
        res = client.get("/api/system/metrics")
        assert res.status_code == 200
        data = res.json()
        assert data["cpu_percent"] == 18.5
        assert data["ram_used_gb"] == 4.25
        assert data["ram_total_gb"] == 16.0
        assert data["ram_percent"] == 26.56


# ==============================================================================
# 3. Testes de WebSocket de Logs (/api/ws/logs)
# ==============================================================================

def test_websocket_logs_lifecycle(client_env):
    client = client_env["client"]
    log_service.add_log("INFO", "Log pré-existente", "startup")

    with patch("backend.services.metrics_service.MetricsService.get_current_metrics") as mock_metrics:
        mock_metrics.return_value = {
            "cpu_percent": 10.0,
            "ram_used_gb": 3.0,
            "ram_total_gb": 16.0,
            "ram_percent": 18.75,
        }

        with client.websocket_connect("/api/ws/logs") as ws:
            # 1. Deve receber o batch inicial com o log pré-existente
            initial_batch = ws.receive_json()
            assert initial_batch["type"] == "log_batch"
            assert len(initial_batch["data"]) == 1
            assert initial_batch["data"][0]["message"] == "Log pré-existente"

            # 2. Transmite novo log enquanto conectado
            log_service.add_log("WARNING", "Aviso em tempo real", "worker")
            new_log_event = ws.receive_json()
            if new_log_event["type"] == "metrics":
                new_log_event = ws.receive_json()
            assert new_log_event["type"] == "log"
            assert new_log_event["data"]["message"] == "Aviso em tempo real"

            # 3. Envia comando do cliente para limpar logs
            ws.send_json({"action": "clear_logs"})
            clear_event = ws.receive_json()
            if clear_event["type"] == "metrics":
                clear_event = ws.receive_json()
            assert clear_event["type"] == "logs_cleared"
            assert len(log_service.get_logs()) == 0


# ==============================================================================
# 4. Testes de Narração com Controles Vocais
# ==============================================================================

def test_narrate_with_voice_controls(client_env):
    client = client_env["client"]
    v_store = client_env["voice_store"]
    sample_p = client_env["voices_dir"] / "locutor_control.wav"
    sample_p.write_bytes(b"sample audio")
    voice = v_store.add_voice("Locutor Controles", str(sample_p), is_default=True)

    with patch("backend.services.tts_service.TTSService.generate_speech") as mock_gen:
        def fake_gen(text, voice_sample_path, output_mp3_path, progress_callback=None,
                     speed=1.0, max_pause=0.3, pitch=0.0, presence=0.5):
            Path(output_mp3_path).write_bytes(b"fake_mp3")
            return Path(output_mp3_path)

        mock_gen.side_effect = fake_gen

        payload = {
            "text": "Texto com controle vocal",
            "voice_id": voice.id,
            "speed": 1.25,
            "max_pause": 0.45,
            "pitch": 2.5,
            "presence": 0.8,
        }
        res = client.post("/api/narrate", json=payload)
        assert res.status_code == 202
        task_id = res.json()["task_id"]

        # Verifica chamada ao TTS com os novos parâmetros
        mock_gen.assert_called_once()
        _, kwargs = mock_gen.call_args
        assert kwargs["speed"] == 1.25
        assert kwargs["max_pause"] == 0.45
        assert kwargs["pitch"] == 2.5
        assert kwargs["presence"] == 0.8

        # Verifica se os parâmetros foram salvos no HistoryStore
        h_store = client_env["history_store"]
        items = h_store.list_history()
        assert len(items) == 1
        item = items[0]
        assert item.speed == 1.25
        assert item.max_pause == 0.45
        assert item.pitch == 2.5
        assert item.presence == 0.8


def test_narrate_and_transcribe_with_voice_controls(client_env):
    client = client_env["client"]
    v_store = client_env["voice_store"]
    sample_p = client_env["voices_dir"] / "locutor_control2.wav"
    sample_p.write_bytes(b"sample audio 2")
    voice = v_store.add_voice("Locutor Controles 2", str(sample_p), is_default=True)

    with patch("backend.services.tts_service.TTSService.generate_speech") as mock_tts, \
         patch("backend.services.stt_service.STTService.transcribe_audio") as mock_stt:

        def fake_tts(text, voice_sample_path, output_mp3_path, progress_callback=None,
                     speed=1.0, max_pause=0.3, pitch=0.0, presence=0.5):
            Path(output_mp3_path).write_bytes(b"mp3_data")
            return Path(output_mp3_path)

        def fake_stt(audio_path, mode=TranscriptionMode.NORMAL, mode_config=None, progress_callback=None):
            return "1\n00:00:00,000 --> 00:00:02,000\nTexto narrado", [
                WordTimestamp(word="Texto", start=0.0, end=1.0, probability=0.99),
                WordTimestamp(word="narrado", start=1.0, end=2.0, probability=0.98),
            ], 2.0

        mock_tts.side_effect = fake_tts
        mock_stt.side_effect = fake_stt

        payload = {
            "text": "Texto para narrar e transcrever",
            "voice_id": voice.id,
            "mode": "dynamic",
            "speed": 0.85,
            "max_pause": 0.2,
            "pitch": -1.5,
            "presence": 0.65,
        }
        res = client.post("/api/narrate-and-transcribe", json=payload)
        assert res.status_code == 202

        # Verifica chamada ao TTS com os novos parâmetros
        mock_tts.assert_called_once()
        _, kwargs = mock_tts.call_args
        assert kwargs["speed"] == 0.85
        assert kwargs["max_pause"] == 0.2
        assert kwargs["pitch"] == -1.5
        assert kwargs["presence"] == 0.65

        # Verifica se os parâmetros foram salvos no HistoryStore
        h_store = client_env["history_store"]
        items = h_store.list_history()
        assert len(items) == 1
        item = items[0]
        assert item.speed == 0.85
        assert item.max_pause == 0.2
        assert item.pitch == -1.5
        assert item.presence == 0.65
        assert item.mode == TranscriptionMode.DYNAMIC
