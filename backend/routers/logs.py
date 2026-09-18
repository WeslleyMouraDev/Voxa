import asyncio
from typing import List, Optional

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from backend.models.schemas import LogEntrySchema
from backend.services.log_service import log_service
from backend.services.metrics_service import MetricsService

router = APIRouter(prefix="/api", tags=["logs"])


@router.get("/logs", response_model=List[LogEntrySchema])
def get_logs(
    level: Optional[str] = None,
    search: Optional[str] = None,
    limit: Optional[int] = Query(default=100, ge=1, le=1000),
) -> List[LogEntrySchema]:
    """
    Retorna o histórico estruturado de logs em memória do ring buffer,
    com suporte a filtros por nível (INFO, WARNING, ERROR), busca textual e limite.
    """
    return log_service.get_logs(level=level, search=search, limit=limit)


@router.delete("/logs")
def clear_logs() -> dict:
    """
    Limpa todos os logs em memória do ring buffer e emite broadcast
    aos clientes conectados informando a limpeza.
    """
    log_service.clear()
    return {"message": "Logs limpos com sucesso"}


@router.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket) -> None:
    """
    Endpoint WebSocket para streaming bidirecional de logs e telemetria:
    - Envia lote inicial de logs ao conectar.
    - Emite novos logs estruturados em tempo real.
    - Emite métricas de hardware a cada 2 segundos.
    - Recebe comandos do cliente (ex: {"action": "clear_logs"}).
    - Trata desconexões com encerramento seguro de tarefas assíncronas.
    """
    await websocket.accept()

    stop_event = asyncio.Event()
    send_lock = asyncio.Lock()

    async def safe_send(payload: dict) -> None:
        async with send_lock:
            await websocket.send_json(payload)

    async def metrics_publisher() -> None:
        try:
            while not stop_event.is_set():
                await asyncio.sleep(2.0)
                if stop_event.is_set():
                    break
                metrics = MetricsService.get_current_metrics()
                await safe_send({"type": "metrics", "data": metrics})
        except (WebSocketDisconnect, asyncio.CancelledError):
            pass
        except Exception:
            pass

    async def log_subscriber() -> None:
        try:
            async for event in log_service.subscribe():
                if stop_event.is_set():
                    break
                await safe_send(event)
        except (WebSocketDisconnect, asyncio.CancelledError):
            pass
        except Exception:
            pass

    async def client_listener() -> None:
        try:
            while not stop_event.is_set():
                data = await websocket.receive_json()
                if isinstance(data, dict) and data.get("action") == "clear_logs":
                    log_service.clear()
        except (WebSocketDisconnect, asyncio.CancelledError):
            pass
        except Exception:
            pass

    metrics_task = asyncio.create_task(metrics_publisher())
    logs_task = asyncio.create_task(log_subscriber())
    listener_task = asyncio.create_task(client_listener())

    tasks = [metrics_task, logs_task, listener_task]
    try:
        await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    finally:
        stop_event.set()
        for t in tasks:
            if not t.done():
                t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
