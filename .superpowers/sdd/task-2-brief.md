# Task 2: Limitador de Recursos de CPU e Gerenciador de Tarefas em Background (SSE)

## Objetivo
Implementar o limitador de recursos da máquina (`CPULimiter`) para garantir que o processo não congele a CPU nem cause lentidão no sistema operacional, e o gerenciador assíncrono de tarefas (`TaskManager`) com streaming de progresso em tempo real via Server-Sent Events (SSE).

## Arquivos a Criar
- `backend/services/__init__.py`
- `backend/services/cpu_limiter.py`
- `backend/services/task_manager.py`
- `tests/test_cpu_limiter.py`
- `tests/test_task_manager.py`

## Especificações Técnicas e Interfaces

### 1. `backend/services/cpu_limiter.py`
- Classe `CPULimiter`:
  - `calculate_threads(cpu_percent: int) -> int`:
    - Obtém o total de CPUs lógicas via `os.cpu_count()` ou `psutil.cpu_count(logical=True)`.
    - Calcula `max(1, int(total_cores * (cpu_percent / 100.0)))`.
  - `apply_limits(cpu_percent: int = 75) -> dict`:
    - Aplica limite de threads no PyTorch se importável (`torch.set_num_threads(n_threads)`). Se PyTorch não estiver instalado ou falhar, captura graciosamente sem quebrar.
    - Aplica prioridade baixa no processo atual via `psutil.Process()`:
      - No Windows (`os.name == 'nt'`): `p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)`.
      - No Linux/Unix: `p.nice(10)` (ou fallback se permissão for negada).
    - Retorna dict com `{"cpu_percent": cpu_percent, "threads": n_threads, "total_cores": total_cores, "nice_applied": bool}`.

### 2. `backend/services/task_manager.py`
- Gerenciador singleton ou classe `TaskManager`:
  - Modos de tarefa assíncrona: rastreia ID de tarefa, status (`TaskStatus`), progresso numérico (0.0 a 100.0), mensagem de status, resultado e erro.
  - `create_task(name: str = "") -> str`: gera UUID `task_id`, inicializa status como `TaskStatus.PROCESSING`, progresso 0.0, cria `asyncio.Queue` para ouvintes SSE.
  - `update_progress(task_id: str, progress: float, message: str) -> None`: atualiza progresso (0-100) e mensagem, emite evento para ouvintes.
  - `complete_task(task_id: str, result: dict) -> None`: define status como `TaskStatus.COMPLETED`, progresso 100.0, emite evento final para ouvintes e limpa recursos.
  - `fail_task(task_id: str, error: str) -> None`: define status como `TaskStatus.ERROR`, emite evento de erro para ouvintes.
  - `get_task(task_id: str) -> Optional[dict]`: retorna dados da tarefa.
  - `subscribe(task_id: str) -> AsyncGenerator[dict, None]`: gerador assíncrono que consome da fila da tarefa e faz `yield` dos eventos até a tarefa ser concluída ou falhar (SSE ready).

## Requisitos de Testes
- `tests/test_cpu_limiter.py`:
  - Testar cálculo correto de threads para 25%, 50%, 75%, 100%.
  - Testar execução de `apply_limits` sem erros (mesmo sem torch ou com mock de psutil).
- `tests/test_task_manager.py`:
  - Testar criação de tarefa, fluxo de `update_progress`, `complete_task`, `fail_task`.
  - Testar o gerador assíncrono `subscribe` com simulação de eventos em sequência.

## Comandos
- Testes: `python -m pytest tests/test_cpu_limiter.py tests/test_task_manager.py -v`
- Commits: `git add backend/services/ tests/test_cpu_limiter.py tests/test_task_manager.py && git commit -m "feat: add cpu limiter and async background task manager with sse"`
