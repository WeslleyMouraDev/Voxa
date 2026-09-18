# Task 2 Brief: Serviços de Captura de Logs e Coleta de Métricas

## Objetivo
Implementar o serviço de ring buffer de logs com interceptador de logs do Python (`LogBufferHandler`), interceptador de streams (`StreamInterceptor`) e o serviço de coleta de métricas de sistema (`MetricsService`) usando `psutil`.

## Arquivos a Criar
- `backend/services/log_service.py`
- `backend/services/metrics_service.py`
- `tests/test_log_service.py`
- `tests/test_metrics_service.py`
- Relatório: `d:\Projetos\Voxa\.superpowers\sdd\task-2-report.md`

## Requisitos Técnicos

### 1. `backend/services/log_service.py`
- Importar `collections.deque`, `threading.Lock`, `asyncio`, `logging`, `datetime`, `timezone`, etc.
- Classe `LogService`:
  - `__init__(self, max_entries: int = 1000)`:
    - `self._max_entries = max_entries`
    - `self._buffer = deque(maxlen=max_entries)`
    - `self._lock = Lock()`
    - `self._counter = 0`
    - `self._subscribers: list[asyncio.Queue] = []`
  - `add_log(self, level: str, message: str, source: str = "app") -> dict`:
    - Incrementa `_counter` sob lock.
    - Timestamp no formato ISO UTC: `datetime.now(timezone.utc).isoformat()`.
    - Sanitiza `message` (remove quebras de linha residuais no final). Se a mensagem for vazia ou apenas whitespace, pode ignorar.
    - Entry: `{"id": self._counter, "timestamp": ts, "level": level.upper(), "message": message, "source": source}`.
    - Adiciona ao `_buffer` sob lock.
    - Emite para ouvintes (broadcast threadsafe similar ao `TaskManager._broadcast`).
    - Retorna a entrada criada.
  - `get_logs(self, level: Optional[str] = None, search: Optional[str] = None, limit: Optional[int] = None) -> list[dict]`:
    - Retorna cópia dos logs sob lock.
    - Suporta filtro por `level` (case-insensitive, ex: "ERROR").
    - Suporta filtro por substring em `search` (case-insensitive dentro de `message` ou `source`).
    - Aplica `limit` se fornecido (retorna os últimos `limit` logs).
  - `clear(self) -> None`:
    - Esvazia `_buffer` e notifica subscribers com evento `{"type": "logs_cleared"}`.
  - Inscrição assíncrona:
    - `subscribe(self) -> AsyncGenerator[dict, None]`: registra queue, entrega histórico inicial em lote (`{"type": "log_batch", "data": list_of_logs}`) e depois cede novos logs individuais conforme chegam.
  - Singleton `log_service = LogService()`.

- Classe `LogBufferHandler(logging.Handler)`:
  - Recebe `service: Optional[LogService] = None` (se None, usa `log_service`).
  - Em `emit(self, record: logging.LogRecord)`:
    - Extrai mensagem formatada `msg = self.format(record)`.
    - Mapeia `record.levelname` para `level`.
    - Chama `service.add_log(level=record.levelname, message=msg, source=record.name)`.

- Classe `StreamInterceptor`:
  - Utilitário para duplicar `sys.stdout` e `sys.stderr`.
  - Guarda `original_stream` e `service`.
  - Método `write(text)`: escreve no `original_stream` E, se houver linhas não vazias, envia para `service.add_log(level="INFO"|"ERROR", message=line, source=self.source_name)`.
  - Método `flush()`: chama `original_stream.flush()`.
  - Fornecer métodos auxiliares `isatty()`, `fileno()` delegando para `original_stream` caso existam.

### 2. `backend/services/metrics_service.py`
- Importar `psutil`.
- Classe `MetricsService`:
  - Método estático ou de classe `get_current_metrics() -> dict`:
    - Coleta `cpu_percent = float(psutil.cpu_percent(interval=None))`
    - Coleta `mem = psutil.virtual_memory()`
    - `ram_used_gb = round(mem.used / (1024 ** 3), 2)`
    - `ram_total_gb = round(mem.total / (1024 ** 3), 2)`
    - `ram_percent = float(mem.percent)`
    - Retorna `{"cpu_percent": cpu_percent, "ram_used_gb": ram_used_gb, "ram_total_gb": ram_total_gb, "ram_percent": ram_percent}`

### 3. Ciclo TDD
- Criar `tests/test_log_service.py` e `tests/test_metrics_service.py`.
- Rodar `.venv\Scripts\python.exe -m pytest tests/test_log_service.py tests/test_metrics_service.py -v` (confirmar falha).
- Implementar `backend/services/log_service.py` e `backend/services/metrics_service.py`.
- Executar testes novamente até 100% verde.
- Executar toda a suíte de testes (`.venv\Scripts\python.exe -m pytest tests/ -v`) para garantir zero regressões.
- Fazer commit git: `feat(services): implement log buffer handler and system metrics collector`.
