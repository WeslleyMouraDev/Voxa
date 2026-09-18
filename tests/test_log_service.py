import asyncio
import io
import logging
import threading
import pytest
from datetime import datetime

from backend.services.log_service import (
    LogService,
    LogBufferHandler,
    StreamInterceptor,
    log_service,
)
from backend.models.schemas import LogEntrySchema


def test_log_service_ring_buffer():
    service = LogService(max_entries=5)
    for i in range(10):
        service.add_log(level="INFO", message=f"Mensagem {i}", source="test")

    logs = service.get_logs()
    assert len(logs) == 5
    assert logs[0]["message"] == "Mensagem 5"
    assert logs[-1]["message"] == "Mensagem 9"


def test_log_service_entry_structure():
    service = LogService(max_entries=10)
    entry = service.add_log(level="info", message="Teste estrutural", source="api")

    assert entry is not None
    assert entry["id"] == 1
    assert entry["level"] == "INFO"
    assert entry["message"] == "Teste estrutural"
    assert entry["source"] == "api"

    # Valida formato ISO do timestamp
    ts = datetime.fromisoformat(entry["timestamp"])
    assert ts is not None

    # Valida compatibilidade com o schema pydantic
    schema_model = LogEntrySchema(**entry)
    assert schema_model.id == 1
    assert schema_model.level == "INFO"


def test_log_service_sanitization():
    service = LogService(max_entries=10)

    # Quebras de linha residuais no final devem ser removidas
    e1 = service.add_log(level="INFO", message="Linha com quebra\r\n", source="test")
    assert e1 is not None
    assert e1["message"] == "Linha com quebra"

    # Mensagens vazias ou apenas espaços devem ser ignoradas
    e2 = service.add_log(level="INFO", message="", source="test")
    assert e2 is None

    e3 = service.add_log(level="INFO", message="   \n\r\t  ", source="test")
    assert e3 is None

    assert len(service.get_logs()) == 1


def test_log_service_filter_level():
    service = LogService(max_entries=10)
    service.add_log("INFO", "Info msg", "test")
    service.add_log("ERROR", "Error msg 1", "test")
    service.add_log("WARNING", "Warn msg", "test")
    service.add_log("error", "Error msg 2", "test")

    errors = service.get_logs(level="error")
    assert len(errors) == 2
    assert errors[0]["message"] == "Error msg 1"
    assert errors[1]["message"] == "Error msg 2"

    warns = service.get_logs(level="WARNING")
    assert len(warns) == 1
    assert warns[0]["message"] == "Warn msg"


def test_log_service_filter_search():
    service = LogService(max_entries=10)
    service.add_log("INFO", "Iniciando worker de audio", source="uvicorn")
    service.add_log("DEBUG", "Carregando checkpoint de voz", source="tts_engine")
    service.add_log("ERROR", "Falha de conexão com redis", source="network")

    # Busca no texto da mensagem
    audio_logs = service.get_logs(search="AUDIO")
    assert len(audio_logs) == 1
    assert audio_logs[0]["message"] == "Iniciando worker de audio"

    # Busca no source
    engine_logs = service.get_logs(search="tts_")
    assert len(engine_logs) == 1
    assert engine_logs[0]["source"] == "tts_engine"


def test_log_service_limit():
    service = LogService(max_entries=20)
    for i in range(10):
        service.add_log("INFO", f"Log {i}", "test")

    limited = service.get_logs(limit=3)
    assert len(limited) == 3
    assert limited[0]["message"] == "Log 7"
    assert limited[-1]["message"] == "Log 9"

    zero_limit = service.get_logs(limit=0)
    assert len(zero_limit) == 0


def test_log_service_clear():
    service = LogService()
    service.add_log("INFO", "Test log", "test")
    assert len(service.get_logs()) == 1

    service.clear()
    assert len(service.get_logs()) == 0

    # Alias clear_logs
    service.add_log("INFO", "Test log 2", "test")
    assert len(service.get_logs()) == 1
    service.clear_logs()
    assert len(service.get_logs()) == 0


def test_log_service_thread_safety():
    service = LogService(max_entries=1000)
    threads = []
    logs_per_thread = 50
    thread_count = 10

    def worker(worker_id: int):
        for i in range(logs_per_thread):
            service.add_log("INFO", f"Worker {worker_id} msg {i}", f"worker_{worker_id}")

    for tid in range(thread_count):
        t = threading.Thread(target=worker, args=(tid,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    logs = service.get_logs()
    assert len(logs) == thread_count * logs_per_thread
    ids = [l["id"] for l in logs]
    assert len(ids) == len(set(ids))  # todos os IDs únicos
    assert min(ids) == 1
    assert max(ids) == thread_count * logs_per_thread


def test_log_buffer_handler():
    service = LogService()
    handler = LogBufferHandler(service)
    logger = logging.getLogger("test_buffer_logger")
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    logger.info("Mensagem via logger padrao")
    logger.warning("Alerta via logger padrao")

    logs = service.get_logs()
    assert len(logs) == 2
    assert logs[0]["level"] == "INFO"
    assert "Mensagem via logger padrao" in logs[0]["message"]
    assert logs[0]["source"] == "test_buffer_logger"

    assert logs[1]["level"] == "WARNING"
    assert "Alerta via logger padrao" in logs[1]["message"]


def test_stream_interceptor():
    service = LogService()
    fake_stdout = io.StringIO()
    interceptor = StreamInterceptor(
        original_stream=fake_stdout,
        service=service,
        level="INFO",
        source="stdout",
    )

    interceptor.write("Texto impresso no console\n")
    interceptor.flush()

    # Checa se o stream original recebeu a escrita
    assert "Texto impresso no console\n" in fake_stdout.getvalue()

    # Checa se o buffer do LogService registrou a linha
    logs = service.get_logs()
    assert len(logs) == 1
    assert logs[0]["level"] == "INFO"
    assert logs[0]["message"] == "Texto impresso no console"
    assert logs[0]["source"] == "stdout"

    # Linhas vazias não devem gerar logs
    interceptor.write("\n\n")
    assert len(service.get_logs()) == 1


@pytest.mark.asyncio
async def test_log_service_subscribe():
    service = LogService(max_entries=10)
    service.add_log("INFO", "Log historico 1", "test")
    service.add_log("INFO", "Log historico 2", "test")

    received_events = []

    async def consumer():
        async for event in service.subscribe():
            received_events.append(event)
            if event.get("type") == "logs_cleared":
                break

    task = asyncio.create_task(consumer())
    await asyncio.sleep(0.05)

    # Adiciona novo log durante a assinatura
    service.add_log("WARNING", "Novo log em tempo real", "test")
    await asyncio.sleep(0.05)

    # Limpa logs
    service.clear()
    await asyncio.wait_for(task, timeout=2.0)

    # Verifica eventos recebidos
    assert len(received_events) >= 3
    # 1º evento: batch inicial
    assert received_events[0]["type"] == "log_batch"
    assert len(received_events[0]["data"]) == 2
    assert received_events[0]["data"][0]["message"] == "Log historico 1"

    # 2º evento: novo log
    assert received_events[1]["type"] == "log"
    assert received_events[1]["data"]["message"] == "Novo log em tempo real"

    # 3º evento: logs_cleared
    assert received_events[2]["type"] == "logs_cleared"
