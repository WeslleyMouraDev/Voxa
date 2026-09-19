import json
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from backend.services.task_manager import task_manager

router = APIRouter(prefix="/api/progress", tags=["progress"])


@router.get("/{task_id}")
async def get_progress(task_id: str) -> StreamingResponse:
    """
    Endpoint SSE (Server-Sent Events) para streaming de progresso em tempo real da tarefa.
    """
    task = task_manager.get_task(task_id)
    if task is None:
        async def not_found_generator() -> AsyncGenerator[str, None]:
            payload = json.dumps(
                {
                    "id": task_id,
                    "status": "error",
                    "progress": 0.0,
                    "message": "Tarefa não encontrada ou expirada no servidor",
                    "error": "Tarefa não encontrada ou expirada no servidor",
                },
                ensure_ascii=False,
            )
            yield f"data: {payload}\n\n"

        return StreamingResponse(
            not_found_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "close",
                "X-Accel-Buffering": "no",
            },
        )

    async def event_generator() -> AsyncGenerator[str, None]:
        async for event in task_manager.subscribe(task_id):
            payload = json.dumps(event, ensure_ascii=False)
            yield f"data: {payload}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
