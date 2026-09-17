import asyncio
import pytest

from backend.models.enums import TaskStatus
from backend.services.task_manager import TaskManager


@pytest.mark.asyncio
async def test_create_and_get_task():
    manager = TaskManager()
    task_id = manager.create_task(name="Teste Criar")

    assert isinstance(task_id, str)
    assert len(task_id) > 0

    task = manager.get_task(task_id)
    assert task is not None
    assert task["id"] == task_id
    assert task["name"] == "Teste Criar"
    assert task["status"] == TaskStatus.PROCESSING
    assert task["progress"] == 0.0
    assert task["result"] is None
    assert task["error"] is None


@pytest.mark.asyncio
async def test_update_progress():
    manager = TaskManager()
    task_id = manager.create_task(name="Teste Progresso")

    manager.update_progress(task_id, progress=45.0, message="Convertendo...")
    task = manager.get_task(task_id)

    assert task["progress"] == 45.0
    assert task["message"] == "Convertendo..."
    assert task["status"] == TaskStatus.PROCESSING


@pytest.mark.asyncio
async def test_complete_task():
    manager = TaskManager()
    task_id = manager.create_task(name="Teste Conclusao")

    result_payload = {"audio_path": "audio.wav", "duration": 12.5}
    manager.complete_task(task_id, result=result_payload)

    task = manager.get_task(task_id)
    assert task["status"] == TaskStatus.COMPLETED
    assert task["progress"] == 100.0
    assert task["result"] == result_payload
    assert task["error"] is None


@pytest.mark.asyncio
async def test_fail_task():
    manager = TaskManager()
    task_id = manager.create_task(name="Teste Falha")

    manager.fail_task(task_id, error="Erro de sintetizador")

    task = manager.get_task(task_id)
    assert task["status"] == TaskStatus.ERROR
    assert task["error"] == "Erro de sintetizador"


@pytest.mark.asyncio
async def test_subscribe_lifecycle():
    manager = TaskManager()
    task_id = manager.create_task(name="Teste SSE")

    events = []

    async def worker():
        await asyncio.sleep(0.01)
        manager.update_progress(task_id, 25.0, "Etapa 1")
        await asyncio.sleep(0.01)
        manager.update_progress(task_id, 75.0, "Etapa 2")
        await asyncio.sleep(0.01)
        manager.complete_task(task_id, result={"status": "ok"})

    async def listener():
        async for event in manager.subscribe(task_id):
            events.append(event)

    await asyncio.gather(worker(), listener())

    assert len(events) >= 3
    # First event received could be initial state or Etapa 1
    assert any(e["progress"] == 25.0 and e["message"] == "Etapa 1" for e in events)
    assert any(e["progress"] == 75.0 and e["message"] == "Etapa 2" for e in events)
    last_event = events[-1]
    assert last_event["status"] == TaskStatus.COMPLETED
    assert last_event["progress"] == 100.0
    assert last_event["result"] == {"status": "ok"}


@pytest.mark.asyncio
async def test_subscribe_fail_lifecycle():
    manager = TaskManager()
    task_id = manager.create_task(name="Teste SSE Falha")

    events = []

    async def worker():
        await asyncio.sleep(0.01)
        manager.update_progress(task_id, 30.0, "Processando...")
        await asyncio.sleep(0.01)
        manager.fail_task(task_id, error="Falha fatal")

    async def listener():
        async for event in manager.subscribe(task_id):
            events.append(event)

    await asyncio.gather(worker(), listener())

    assert len(events) >= 2
    last_event = events[-1]
    assert last_event["status"] == TaskStatus.ERROR
    assert last_event["error"] == "Falha fatal"


@pytest.mark.asyncio
async def test_subscribe_multiple_listeners():
    manager = TaskManager()
    task_id = manager.create_task(name="Teste Multi Ouvintes")

    events_a = []
    events_b = []

    async def worker():
        await asyncio.sleep(0.01)
        manager.update_progress(task_id, 50.0, "Meio do caminho")
        await asyncio.sleep(0.01)
        manager.complete_task(task_id, result={"done": True})

    async def listener_a():
        async for event in manager.subscribe(task_id):
            events_a.append(event)

    async def listener_b():
        async for event in manager.subscribe(task_id):
            events_b.append(event)

    await asyncio.gather(worker(), listener_a(), listener_b())

    assert len(events_a) >= 2
    assert len(events_b) >= 2
    assert events_a[-1]["status"] == TaskStatus.COMPLETED
    assert events_b[-1]["status"] == TaskStatus.COMPLETED
