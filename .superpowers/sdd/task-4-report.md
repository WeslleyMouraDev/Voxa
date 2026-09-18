# Relatório da Task 4: Endpoints REST e WebSocket de Logs, Métricas e Narração Atualizada

## Visão Geral
- **Data:** 18/09/2026
- **Status:** Concluído com sucesso (DONE)
- **Commit:** `e126358` (`feat(api): add logs websocket, system metrics and update narration with voice controls`)

## Alterações Realizadas

### 1. `backend/routers/logs.py` (Novo)
- `GET /api/logs`:
  - Retorna `List[LogEntrySchema]`.
  - Parâmetros de consulta validados: `level: Optional[str] = None`, `search: Optional[str] = None`, `limit: Optional[int] = Query(default=100, ge=1, le=1000)`.
  - Integração com `log_service.get_logs(...)`.
- `DELETE /api/logs`:
  - Esvazia o buffer de logs via `log_service.clear()`.
  - Retorna `{"message": "Logs limpos com sucesso"}` e dispara broadcast `logs_cleared`.
- `WebSocket /api/ws/logs`:
  - Aceita conexão e transmite imediatamente o lote inicial de histórico (`{"type": "log_batch", "data": [...]}`).
  - Monitora o gerador `log_service.subscribe()` para emitir logs individuais em tempo real (`{"type": "log", "data": {...}}`).
  - Publicador periódico de telemetria emitindo métricas de hardware a cada 2 segundos (`{"type": "metrics", "data": metrics}`).
  - Receptor de mensagens do cliente (ex: `{"action": "clear_logs"}`) disparando a limpeza do buffer.
  - Sincronização segura de escrita via `asyncio.Lock` e encerramento limpo de tarefas assíncronas ao desconectar (`WebSocketDisconnect`).

### 2. `backend/routers/system.py` (Novo)
- `GET /api/system/metrics`:
  - Retorna `SystemMetricsSchema` (`cpu_percent`, `ram_used_gb`, `ram_total_gb`, `ram_percent`).
  - Integração direta com `MetricsService.get_current_metrics()`.

### 3. `backend/routers/narration.py`
- Atualização das tarefas assíncronas `_run_narration_task` e `_run_narrate_and_transcribe_task`:
  - Aceitação dos novos parâmetros: `speed: float = 1.0`, `max_pause: float = 0.3`, `pitch: float = 0.0`, `presence: float = 0.5`.
  - Helper `_invoke_tts_generate` com reflexão via `inspect.signature` para repassar os novos parâmetros preservando retrocompatibilidade com mocks legados.
  - Armazenamento completo dos controles nos registros do `HistoryItemSchema`.
- Atualização dos endpoints `POST /api/narrate` e `POST /api/narrate-and-transcribe`:
  - Repasse de `request.speed`, `request.max_pause`, `request.pitch` e `request.presence` para as tarefas em background.

### 4. `backend/main.py`
- Registro dos novos roteadores `logs.router` e `system.router`.
- Função `setup_logging()` acoplada ao lifecycle da aplicação, anexando o `LogBufferHandler` aos loggers raiz (`logging.getLogger()`) e do servidor uvicorn (`uvicorn`, `uvicorn.access`, `uvicorn.error`).
- Enriquecimento da documentação OpenAPI/Swagger com metadados detalhados de tags em PT-BR (`OPENAPI_TAGS`) e descrição contextualizada da API Voxa.

### 5. `tests/test_logs_api.py` (Novo)
- 8 testes cobrindo todo o ciclo de vida dos novos endpoints:
  1. `test_get_logs_empty`: validação de lista vazia.
  2. `test_get_logs_with_filtering_and_limit`: validação de filtros por level, busca textual e paginação por limit.
  3. `test_get_logs_limit_validation`: rejeição com HTTP 422 para limites inválidos (<= 0 ou > 1000).
  4. `test_delete_logs`: limpeza do ring buffer e confirmação.
  5. `test_get_system_metrics`: validação do payload de métricas de sistema.
  6. `test_websocket_logs_lifecycle`: ciclo completo de conexão, recebimento de histórico, logs em tempo real, métricas e comando `clear_logs`.
  7. `test_narrate_with_voice_controls`: validação de repasse dos controles de voz para o TTS e gravação no histórico.
  8. `test_narrate_and_transcribe_with_voice_controls`: validação com narração, transcrição e controles vocais.

## Ciclo TDD e Verificação

1. **RED (Fase de Falha Inicial):**
   - Comando: `.venv\Scripts\python.exe -m pytest tests/test_logs_api.py -v`
   - Resultado: 8 falhas esperadas (rotas inexistentes e ausência dos parâmetros).
2. **GREEN (Fase de Implementação):**
   - Comando: `.venv\Scripts\python.exe -m pytest tests/test_logs_api.py -v`
   - Resultado: 8 passed em 1.05s.
3. **Regressão Completa da Suíte:**
   - Comando: `.venv\Scripts\python.exe -m pytest tests/ -v`
   - Resultado: 130 passed em 25.43s (zero regressões nos 122 testes prévios).
4. **Knowledge Graph:**
   - Atualizado via `graphify update .` (731 nós, 937 arestas, 71 comunidades).

## Preocupações / Observações
- O endpoint WebSocket utiliza `asyncio.Lock` dedicado para evitar envio concorrente desordenado entre o loop de métricas e o gerador de logs.
- O helper `_invoke_tts_generate` garante resiliência completa para chamadas onde executores ou mocks não definam explicitamente parâmetros adicionais.
