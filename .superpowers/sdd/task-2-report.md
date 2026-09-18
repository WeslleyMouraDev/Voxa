# Relatório da Task 2: Serviços de Captura de Logs e Coleta de Métricas

## Visão Geral
- **Data:** 18/09/2026
- **Status:** Concluído com sucesso (DONE)
- **Commit:** `9b87b4a` (`feat(services): implement log buffer handler and system metrics collector`)

## Alterações Realizadas

### 1. `backend/services/log_service.py` (Novo)
- **`LogService`**:
  - Ring buffer em memória thread-safe baseado em `collections.deque(maxlen=max_entries)`.
  - Controle de concorrência com `threading.Lock`.
  - `add_log(level, message, source="app")`: incrementa ID atômico, timestamp UTC ISO, sanitização de quebras de linha (`\r\n`), descarte de mensagens vazias/whitespace, broadcast thread-safe para filas assíncronas.
  - `broadcast_log(entry)`: utilitário para emissão direta de eventos de log.
  - `get_logs(level=None, search=None, limit=None)`: filtragem flexível case-insensitive por nível e termo de busca (mensagem ou origem), fatiamento por limite.
  - `clear()` e alias `clear_logs()`: esvazia buffer e notifica assinantes com evento `{"type": "logs_cleared"}`.
  - `subscribe()`: gerador assíncrono entregando lote inicial (`{"type": "log_batch", "data": ...}`) e novos eventos em tempo real com limpeza no encerramento.
  - Singleton `log_service = LogService()`.
- **`LogBufferHandler(logging.Handler)`**:
  - Interceptador integrado ao subsistema de logging do Python que redireciona logs para o `LogService`.
- **`StreamInterceptor(io.TextIOBase)`**:
  - Interceptador e duplicador de fluxos de console (`sys.stdout`/`sys.stderr`), repassando para o stream original e gerando logs para linhas não vazias com delegação de `flush`, `isatty` e `fileno`.

### 2. `backend/services/metrics_service.py` (Novo)
- **`MetricsService`**:
  - Método de classe `get_current_metrics()` integrando `psutil`:
    - `cpu_percent`: percentual de uso de CPU (`psutil.cpu_percent(interval=None)`).
    - `ram_used_gb`: memória utilizada em gigabytes arredondada para 2 casas decimais.
    - `ram_total_gb`: memória total do sistema em gigabytes arredondada para 2 casas decimais.
    - `ram_percent`: percentual de utilização da memória RAM.
    - Compatível diretamente com `SystemMetricsSchema`.

### 3. `tests/test_log_service.py` (Novo)
- 11 testes cobrindo ring buffer, sanitização, descarte de vazio, filtros por nível e busca textual, limites, limpeza, concorrência com múltiplas threads (`test_log_service_thread_safety`), `LogBufferHandler`, `StreamInterceptor` e ciclo de vida assíncrono de `subscribe`.

### 4. `tests/test_metrics_service.py` (Novo)
- 2 testes cobrindo medições reais de sistema e validação matemática/arredondamentos com mocks de `psutil`.

## Ciclo TDD e Verificação

1. **RED (Fase de Falha):**
   - Execução: `.venv\Scripts\python.exe -m pytest tests/test_log_service.py tests/test_metrics_service.py -v`
   - Resultado: 2 falhas esperadas (`ModuleNotFoundError: No module named 'backend.services.log_service'`).
2. **GREEN (Fase de Implementação e Sucesso):**
   - Execução: `.venv\Scripts\python.exe -m pytest tests/test_log_service.py tests/test_metrics_service.py -v`
   - Resultado: 13 testes passaram em 0.79s (100% verde).
3. **Regressão Completa:**
   - Execução: `.venv\Scripts\python.exe -m pytest tests/ -v`
   - Resultado: 117 testes passaram (100% verde, zero regressões).
4. **Knowledge Graph:**
   - Atualizado via `graphify update .` (656 nós, 851 arestas, 66 comunidades).

## Preocupações / Observações
- O `StreamInterceptor` delega operações de console de forma resiliente, mas na inicialização do servidor em produção deve ser aplicado apenas quando a captura de stdout/stderr for explicitamente ativada no ciclo de vida da aplicação FastAPI.
