import asyncio
import copy
from collections import deque
from datetime import datetime, timezone
import io
import logging
from threading import Lock
from typing import Any, AsyncGenerator, Dict, List, Optional


class LogService:
    """
    Serviço thread-safe de ring buffer em memória para captura e streaming
    de logs estruturados em tempo real.
    """

    def __init__(self, max_entries: int = 1000) -> None:
        self._max_entries = max(1, max_entries)
        self._buffer: deque[Dict[str, Any]] = deque(maxlen=self._max_entries)
        self._lock = Lock()
        self._counter = 0
        self._subscribers: List[asyncio.Queue] = []

    def add_log(
        self,
        level: str,
        message: str,
        source: str = "app",
    ) -> Optional[Dict[str, Any]]:
        """
        Adiciona uma nova entrada de log ao ring buffer e transmite para ouvintes.
        Ignora mensagens vazias ou constituídas unicamente por espaços.
        """
        if message is None:
            return None

        clean_message = message.rstrip("\r\n")
        if not clean_message.strip():
            return None

        ts = datetime.now(timezone.utc).isoformat()
        with self._lock:
            self._counter += 1
            entry: Dict[str, Any] = {
                "id": self._counter,
                "timestamp": ts,
                "level": level.strip().upper(),
                "message": clean_message,
                "source": source,
            }
            self._buffer.append(entry)

        # Broadcast para assinantes em tempo real
        self._broadcast({"type": "log", "data": copy.deepcopy(entry), **entry})
        return copy.deepcopy(entry)

    def broadcast_log(self, entry: Dict[str, Any]) -> None:
        """
        Transmite uma entrada de log para os ouvintes conectados.
        """
        self._broadcast({"type": "log", "data": copy.deepcopy(entry), **entry})

    def _broadcast(self, event: Dict[str, Any]) -> None:
        """
        Distribuição segura entre threads e event loops para assinantes.
        """
        with self._lock:
            queues = list(self._subscribers)

        for q in queues:
            try:
                try:
                    current_loop = asyncio.get_running_loop()
                except RuntimeError:
                    current_loop = None

                loop = getattr(q, "_loop", None)
                if loop and loop.is_running() and current_loop != loop:
                    loop.call_soon_threadsafe(q.put_nowait, event)
                else:
                    q.put_nowait(event)
            except Exception:
                pass

    def get_logs(
        self,
        level: Optional[str] = None,
        search: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retorna snapshot filtrado dos logs armazenados no buffer.
        """
        with self._lock:
            logs = [copy.deepcopy(entry) for entry in self._buffer]

        if level:
            lvl = level.strip().upper()
            logs = [entry for entry in logs if entry.get("level") == lvl]

        if search:
            term = search.lower()
            logs = [
                entry
                for entry in logs
                if term in entry.get("message", "").lower()
                or term in entry.get("source", "").lower()
            ]

        if limit is not None:
            if limit <= 0:
                return []
            logs = logs[-limit:]

        return logs

    def clear(self) -> None:
        """
        Limpa todos os logs do buffer e notifica os assinantes.
        """
        with self._lock:
            self._buffer.clear()
        self._broadcast({"type": "logs_cleared"})

    def clear_logs(self) -> None:
        """Alias de compatibilidade para clear."""
        self.clear()

    async def subscribe(self) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Gerador assíncrono que entrega o histórico inicial em lote
        e novos logs/eventos conforme chegam.
        """
        queue: asyncio.Queue = asyncio.Queue()
        with self._lock:
            self._subscribers.append(queue)

        try:
            initial_logs = self.get_logs()
            yield {"type": "log_batch", "data": initial_logs}

            while True:
                event = await queue.get()
                yield event
        finally:
            with self._lock:
                if queue in self._subscribers:
                    self._subscribers.remove(queue)


class LogBufferHandler(logging.Handler):
    """
    Handler do logging nativo do Python que envia logs para o LogService.
    """

    def __init__(self, service: Optional[LogService] = None) -> None:
        super().__init__()
        self.service = service or log_service

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            self.service.add_log(
                level=record.levelname,
                message=msg,
                source=record.name,
            )
        except Exception:
            self.handleError(record)


class StreamInterceptor(io.TextIOBase):
    """
    Interceptador de fluxos de texto (stdout/stderr) que duplica saídas para
    o console original e encaminha linhas não-vazias para o LogService.
    """

    def __init__(
        self,
        original_stream: Any,
        service: Optional[LogService] = None,
        level: str = "INFO",
        source: str = "stdout",
    ) -> None:
        super().__init__()
        self.original_stream = original_stream
        self.service = service or log_service
        self.level = level
        self.source_name = source

    def write(self, text: str) -> int:
        if self.original_stream and hasattr(self.original_stream, "write"):
            try:
                res = self.original_stream.write(text)
            except Exception:
                res = len(text) if text else 0
        else:
            res = len(text) if text else 0

        if text:
            for line in text.splitlines():
                clean = line.rstrip("\r\n")
                if clean.strip():
                    self.service.add_log(
                        level=self.level,
                        message=clean,
                        source=self.source_name,
                    )
        return res

    def flush(self) -> None:
        if self.original_stream and hasattr(self.original_stream, "flush"):
            try:
                self.original_stream.flush()
            except Exception:
                pass

    def isatty(self) -> bool:
        if self.original_stream and hasattr(self.original_stream, "isatty"):
            try:
                return bool(self.original_stream.isatty())
            except Exception:
                return False
        return False

    def fileno(self) -> int:
        if self.original_stream and hasattr(self.original_stream, "fileno"):
            return self.original_stream.fileno()
        raise io.UnsupportedOperation("fileno")

    def readable(self) -> bool:
        return False

    def writable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return False


# Singleton padrão do serviço de logs
log_service = LogService()
