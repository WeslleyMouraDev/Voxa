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
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")

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
