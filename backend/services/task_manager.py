import asyncio
import copy
import uuid
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Dict, List, Optional

from backend.models.enums import TaskStatus


class TaskManager:
    """
    Gerenciador assíncrono de tarefas em segundo plano com suporte a streaming
    de progresso em tempo real (compatível com Server-Sent Events / SSE).
    """

    def __init__(self) -> None:
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._subscribers: Dict[str, List[asyncio.Queue]] = {}

    def create_task(self, name: str = "") -> str:
        """
        Cria e inicializa uma nova tarefa com status PROCESSING e progresso 0.0.
        """
        task_id = str(uuid.uuid4())
        now_str = datetime.now(timezone.utc).isoformat()
        self._tasks[task_id] = {
            "id": task_id,
            "name": name,
            "status": TaskStatus.PROCESSING,
            "progress": 0.0,
            "message": "",
            "result": None,
            "error": None,
            "created_at": now_str,
            "updated_at": now_str,
        }
        self._subscribers[task_id] = []
        return task_id

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Retorna os dados da tarefa ou None se não encontrada.
        """
        task = self._tasks.get(task_id)
        return copy.deepcopy(task) if task is not None else None

    def _broadcast(self, task_id: str) -> None:
        """
        Envia uma cópia do estado atual da tarefa para todos os ouvintes inscritos.
        """
        task = self._tasks.get(task_id)
        if not task:
            return

        snapshot = copy.deepcopy(task)
        queues = self._subscribers.get(task_id, [])

        for q in list(queues):
            try:
                try:
                    current_loop = asyncio.get_running_loop()
                except RuntimeError:
                    current_loop = None

                loop = getattr(q, "_loop", None)
                if loop and loop.is_running() and current_loop != loop:
                    loop.call_soon_threadsafe(q.put_nowait, snapshot)
                else:
                    q.put_nowait(snapshot)
            except Exception:
                pass

    def update_progress(self, task_id: str, progress: float, message: str = "") -> None:
        """
        Atualiza o progresso (0-100) e mensagem da tarefa, notificando subscribers.
        """
        if task_id not in self._tasks:
            return

        task = self._tasks[task_id]
        task["progress"] = max(0.0, min(100.0, float(progress)))
        task["message"] = message
        task["updated_at"] = datetime.now(timezone.utc).isoformat()

        self._broadcast(task_id)

    def complete_task(self, task_id: str, result: Dict[str, Any]) -> None:
        """
        Marca a tarefa como concluída com sucesso, define progresso como 100% e emite resultado.
        """
        if task_id not in self._tasks:
            return

        task = self._tasks[task_id]
        task["status"] = TaskStatus.COMPLETED
        task["progress"] = 100.0
        task["result"] = result
        task["error"] = None
        task["updated_at"] = datetime.now(timezone.utc).isoformat()

        self._broadcast(task_id)

    def fail_task(self, task_id: str, error: str) -> None:
        """
        Marca a tarefa com erro, notificando os ouvintes.
        """
        if task_id not in self._tasks:
            return

        task = self._tasks[task_id]
        task["status"] = TaskStatus.ERROR
        task["error"] = error
        task["updated_at"] = datetime.now(timezone.utc).isoformat()

        self._broadcast(task_id)

    async def subscribe(self, task_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Gerador assíncrono que consome eventos de atualização da tarefa
        até a tarefa ser concluída (COMPLETED) ou falhar (ERROR).
        """
        if task_id not in self._tasks:
            return

        queue: asyncio.Queue = asyncio.Queue()
        if task_id not in self._subscribers:
            self._subscribers[task_id] = []
        self._subscribers[task_id].append(queue)

        try:
            # Emite o estado inicial da tarefa ao se conectar
            initial_state = self.get_task(task_id)
            if initial_state is not None:
                yield initial_state
                if initial_state["status"] in (TaskStatus.COMPLETED, TaskStatus.ERROR):
                    return

            while True:
                event = await queue.get()
                yield event
                if event.get("status") in (TaskStatus.COMPLETED, TaskStatus.ERROR):
                    break
        finally:
            if task_id in self._subscribers and queue in self._subscribers[task_id]:
                self._subscribers[task_id].remove(queue)


# Instância singleton padrão para reutilização no backend
task_manager = TaskManager()
