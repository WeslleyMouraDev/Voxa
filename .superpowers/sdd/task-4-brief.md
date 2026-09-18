# Task 4 Brief: Endpoints REST e WebSocket de Logs, Métricas e Narração Atualizada

## Objetivo
Implementar os roteadores FastAPI de logs (`/api/logs` e `/api/ws/logs`), métricas de sistema (`/api/system/metrics`), atualizar o roteador de narração (`/api/narrate`, `/api/narrate-and-transcribe`) com os novos parâmetros de voz, e configurar `backend/main.py` com documentação Swagger OpenAPI enriquecida e anexação do `LogBufferHandler`.

## Arquivos a Criar / Modificar
- Criar: `backend/routers/logs.py`
- Criar: `backend/routers/system.py`
- Modificar: `backend/routers/narration.py`
- Modificar: `backend/main.py`
- Criar: `tests/test_logs_api.py`
- Relatório: `d:\Projetos\Voxa\.superpowers\sdd\task-4-report.md`

## Requisitos Técnicos

### 1. `backend/routers/logs.py`
- `router = APIRouter(prefix="/api", tags=["logs"])`
- `GET /api/logs` -> `List[LogEntrySchema]`:
  - Query params: `level: Optional[str] = None`, `search: Optional[str] = None`, `limit: Optional[int] = Query(default=100, ge=1, le=1000)`.
  - Retorna `log_service.get_logs(level=level, search=search, limit=limit)`.
- `DELETE /api/logs` -> `dict`:
  - Chama `log_service.clear()`.
  - Retorna `{"message": "Logs limpos com sucesso"}`.
- `WebSocket /api/ws/logs`:
  - `await websocket.accept()`.
  - Envia histórico inicial e novos logs via `log_service.subscribe()`.
  - Executa loop de envio periódico de métricas (`MetricsService.get_current_metrics()`) a cada 2 segundos:
    `{"type": "metrics", "data": metrics}`.
  - Ouve mensagens do cliente (`action == "clear_logs"` -> chama `log_service.clear()`).
  - Trata `WebSocketDisconnect` limpando tasks assíncronas com segurança.

### 2. `backend/routers/system.py`
- `router = APIRouter(prefix="/api/system", tags=["system"])`
- `GET /api/system/metrics` -> `SystemMetricsSchema`:
  - Retorna `MetricsService.get_current_metrics()`.

### 3. `backend/routers/narration.py`
- Atualizar `_run_narration_task` e `_run_narrate_and_transcribe_task` para aceitar:
  `speed: float = 1.0, max_pause: float = 0.3, pitch: float = 0.0, presence: float = 0.5`.
- Repassar esses parâmetros para `tts.generate_speech(...)`.
- Salvar os valores no `HistoryItemSchema`.
- Atualizar endpoints `POST /api/narrate` e `POST /api/narrate-and-transcribe` para passar `request.speed, request.max_pause, request.pitch, request.presence` para as tarefas em background.

### 4. `backend/main.py`
- Importar e registrar `logs.router` e `system.router`.
- Anexar `LogBufferHandler` aos loggers raiz do Python (`logging.getLogger()`) e do uvicorn (`logging.getLogger("uvicorn")`, `logging.getLogger("uvicorn.access")`).
- Enriquecer `FastAPI(...)` com metadados detalhados de tags e descrições em PT-BR para a documentação Swagger OpenAPI.

### 5. Ciclo TDD
- Criar `tests/test_logs_api.py` cobrindo:
  - `GET /api/logs` com filtros e ordenação
  - `DELETE /api/logs`
  - `GET /api/system/metrics`
  - `WebSocket /api/ws/logs` (verificando recebimento de `log_batch` e `metrics`)
  - `POST /api/narrate` e `POST /api/narrate-and-transcribe` aceitando os novos campos
- Rodar os testes para confirmar a falha inicial.
- Implementar e reexecutar até passar 100%.
- Rodar a suíte inteira de testes (`tests/test_api.py`, `tests/test_services.py`, etc.) para assegurar zero regressões.
- Fazer commit git: `feat(api): add logs websocket, system metrics and update narration with voice controls`.
